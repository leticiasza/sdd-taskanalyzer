"""Test harness do TaskAnalyzer (Cenários 1, 2 e casos de borda)."""
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.task_analyzer import TaskValidationError, analyze_tasks  # noqa: E402

UTC = timezone.utc


def dt(hora: int, minuto: int = 0) -> datetime:
    """Cria um datetime UTC em 01/09/2026."""
    return datetime(2026, 9, 1, hora, minuto, tzinfo=UTC)


def tarefa(id_tarefa: int = 1, prioridade: str = "alta", status: str = "concluída", **extra):
    """Cria uma tarefa válida, com possibilidade de sobrescrever campos."""
    base = {
        "id_tarefa": id_tarefa,
        "titulo": f"Tarefa {id_tarefa}",
        "prioridade": prioridade,
        "status": status,
        "data_criacao": dt(7),
        "data_inicio": dt(8),
        "data_conclusao": dt(10) if status == "concluída" else None,
        "prazo": dt(12),
    }
    base.update(extra)
    return base


@pytest.fixture
def lote_valido():
    return [
        tarefa(1, "alta", "concluída", data_conclusao=dt(10), prazo=dt(12)),  # 120 min, no prazo
        tarefa(2, "alta", "concluída", data_conclusao=dt(9), prazo=dt(8, 30)),  # 60 min, atrasada
        tarefa(3, "média", "concluída", data_conclusao=dt(11), prazo=dt(12)),  # 180 min, no prazo
        tarefa(4, "baixa", "pendente"),
        tarefa(5, "baixa", "cancelada"),  # excluída dos cálculos
    ]


# ---------- Cenário 1: sucesso ----------
def test_cenario1_totais(lote_valido):
    r = analyze_tasks(lote_valido)
    assert r["total_tarefas"] == 4
    assert r["quantidade_tarefas"] == 4
    assert r["total_concluidas"] == 3
    assert r["total_pendentes"] == 1


def test_cenario1_tempo_medio_geral(lote_valido):
    r = analyze_tasks(lote_valido)
    assert r["tempo_medio_conclusao_min"] == pytest.approx(120.0)
    assert r["tempo_medio_conclusao_horas"] == pytest.approx(2.0)


def test_cenario1_taxa_atraso(lote_valido):
    r = analyze_tasks(lote_valido)
    assert r["taxa_atraso_percentual"] == pytest.approx(33.33, abs=0.01)


def test_cenario1_indicadores_por_prioridade(lote_valido):
    ind = analyze_tasks(lote_valido)["indicadores_por_prioridade"]
    assert ind["alta"]["tempo_medio_conclusao_horas"] == pytest.approx(1.5)
    assert ind["alta"]["taxa_atraso_percentual"] == pytest.approx(50.0)
    assert ind["média"]["tempo_medio_conclusao_horas"] == pytest.approx(3.0)
    assert ind["média"]["taxa_atraso_percentual"] == pytest.approx(0.0)
    assert ind["baixa"]["total_pendentes"] == 1
    assert ind["baixa"]["tempo_medio_conclusao_horas"] == 0.0


def test_cancelada_excluida_dos_calculos(lote_valido):
    r = analyze_tasks(lote_valido)
    assert r["indicadores_por_prioridade"]["baixa"]["total_tarefas"] == 1


# ---------- Cenário 2: exceções ----------
def test_cenario2_conclusao_anterior_ao_inicio():
    lote = [tarefa(data_inicio=dt(10), data_conclusao=dt(9))]
    with pytest.raises(TaskValidationError):
        analyze_tasks(lote)


def test_cenario2_conclusao_anterior_a_criacao():
    lote = [tarefa(data_criacao=dt(9), data_inicio=None, data_conclusao=dt(8))]
    with pytest.raises(TaskValidationError):
        analyze_tasks(lote)


def test_cenario2_concluida_sem_data_conclusao():
    with pytest.raises(TaskValidationError):
        analyze_tasks([tarefa(data_conclusao=None)])


def test_cenario2_prioridade_invalida():
    with pytest.raises(TaskValidationError):
        analyze_tasks([tarefa(prioridade="urgente")])


def test_cenario2_data_sem_fuso():
    with pytest.raises(TaskValidationError):
        analyze_tasks([tarefa(prazo=datetime(2026, 9, 1, 12))])


# ---------- Casos de borda ----------
def test_borda_lote_vazio():
    r = analyze_tasks([])
    assert r["total_tarefas"] == 0
    assert r["tempo_medio_conclusao_min"] == 0.0
    assert r["tempo_medio_conclusao_horas"] == 0.0
    assert r["taxa_atraso_percentual"] == 0.0


def test_borda_somente_pendentes():
    r = analyze_tasks([tarefa(1, "alta", "pendente"), tarefa(2, "baixa", "pendente")])
    assert r["total_pendentes"] == 2
    assert r["total_concluidas"] == 0
    assert r["tempo_medio_conclusao_horas"] == 0.0
    assert r["taxa_atraso_percentual"] == 0.0


def test_borda_sem_data_inicio_usa_criacao():
    r = analyze_tasks([tarefa(data_inicio=None, data_criacao=dt(8), data_conclusao=dt(9))])
    assert r["tempo_medio_conclusao_min"] == pytest.approx(60.0)