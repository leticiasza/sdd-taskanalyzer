"""Módulo TaskAnalyzer: calcula métricas de desempenho e atraso de tarefas."""
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

PRIORIDADES: tuple[str, ...] = ("baixa", "média", "alta")
STATUS_VALIDOS: tuple[str, ...] = ("concluída", "pendente", "cancelada")

Tarefa = dict[str, Any]
Metricas = dict[str, Any]


class TaskValidationError(Exception):
    """Erro lançado quando os dados de entrada violam o contrato da spec."""


def _validar_data(tarefa: Tarefa, campo: str, obrigatorio: bool) -> datetime | None:
    """Valida um campo de data (datetime com fuso).

    Args:
        tarefa: Tarefa analisada.
        campo: Nome do campo de data.
        obrigatorio: Se o campo deve estar presente.

    Returns:
        O datetime validado ou None, se opcional e ausente.

    Raises:
        TaskValidationError: Se ausente, não for datetime ou não tiver fuso.
    """
    valor = tarefa.get(campo)
    if valor is None:
        if obrigatorio:
            raise TaskValidationError(f"Tarefa {tarefa.get('id_tarefa')}: campo '{campo}' é obrigatório.")
        return None
    if not isinstance(valor, datetime) or valor.tzinfo is None:
        raise TaskValidationError(
            f"Tarefa {tarefa.get('id_tarefa')}: '{campo}' deve ser datetime com fuso (UTC)."
        )
    return valor


def _validar_tarefa(tarefa: Tarefa) -> None:
    """Valida uma tarefa conforme o contrato de entrada.

    Raises:
        TaskValidationError: Se qualquer regra do contrato for violada.
    """
    if not isinstance(tarefa, dict):
        raise TaskValidationError("Cada tarefa deve ser um dicionário.")
    id_tarefa = tarefa.get("id_tarefa")
    if isinstance(id_tarefa, bool) or not isinstance(id_tarefa, int) or id_tarefa <= 0:
        raise TaskValidationError(f"id_tarefa inválido: {id_tarefa!r}.")
    titulo = tarefa.get("titulo")
    if not isinstance(titulo, str) or not titulo.strip() or len(titulo) > 200:
        raise TaskValidationError(f"Tarefa {id_tarefa}: título deve ter de 1 a 200 caracteres.")
    if tarefa.get("prioridade") not in PRIORIDADES:
        raise TaskValidationError(f"Tarefa {id_tarefa}: prioridade inválida.")
    status = tarefa.get("status")
    if status not in STATUS_VALIDOS:
        raise TaskValidationError(f"Tarefa {id_tarefa}: status inválido.")

    criacao = _validar_data(tarefa, "data_criacao", True)
    inicio = _validar_data(tarefa, "data_inicio", False)
    conclusao = _validar_data(tarefa, "data_conclusao", status == "concluída")
    _validar_data(tarefa, "prazo", True)

    if conclusao is not None:
        if inicio is not None and conclusao < inicio:
            raise TaskValidationError(f"Tarefa {id_tarefa}: data_conclusao anterior a data_inicio.")
        if criacao is not None and conclusao < criacao:
            raise TaskValidationError(f"Tarefa {id_tarefa}: data_conclusao anterior a data_criacao.")


def _tempo_conclusao_min(tarefa: Tarefa) -> float:
    """Calcula o tempo de conclusão em minutos (início = data_inicio ou data_criacao)."""
    inicio = tarefa.get("data_inicio") or tarefa["data_criacao"]
    return (tarefa["data_conclusao"] - inicio).total_seconds() / 60


def _media(valores: list[float]) -> float:
    """Média dos valores; retorna 0.0 se a lista estiver vazia (sem divisão por zero)."""
    return sum(valores) / len(valores) if valores else 0.0


def _calcular_metricas(tarefas: list[Tarefa]) -> Metricas:
    """Calcula as métricas de um conjunto de tarefas não canceladas."""
    concluidas = [t for t in tarefas if t["status"] == "concluída"]
    pendentes = [t for t in tarefas if t["status"] == "pendente"]
    tempo_min = _media([_tempo_conclusao_min(t) for t in concluidas])
    atrasadas = sum(1 for t in concluidas if t["data_conclusao"] > t["prazo"])
    taxa = (atrasadas / len(concluidas) * 100) if concluidas else 0.0
    return {
        "total_tarefas": len(tarefas),
        "quantidade_tarefas": len(tarefas),
        "total_concluidas": len(concluidas),
        "total_pendentes": len(pendentes),
        "tempo_medio_conclusao_min": round(tempo_min, 2),
        "tempo_medio_conclusao_horas": round(tempo_min / 60, 2),
        "taxa_atraso_percentual": round(taxa, 2),
    }


def analyze_tasks(tarefas: list[Tarefa]) -> Metricas:
    """Analisa um lote de tarefas e devolve métricas gerais e por prioridade.

    Args:
        tarefas: Lista de tarefas conforme o contrato da especificação.

    Returns:
        Dicionário com as métricas gerais e `indicadores_por_prioridade`.

    Raises:
        TaskValidationError: Se a entrada violar o contrato.
    """
    if not isinstance(tarefas, list):
        raise TaskValidationError("A entrada deve ser uma lista de tarefas.")
    for tarefa in tarefas:
        _validar_tarefa(tarefa)

    ativas = [t for t in tarefas if t["status"] != "cancelada"]
    resultado = _calcular_metricas(ativas)
    resultado["indicadores_por_prioridade"] = {
        prioridade: _calcular_metricas([t for t in ativas if t["prioridade"] == prioridade])
        for prioridade in PRIORIDADES
    }
    logger.info("Análise concluída: %d tarefas consideradas.", len(ativas))
    return resultado