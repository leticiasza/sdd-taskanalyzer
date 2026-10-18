# Especificação SDD — TaskAnalyzer (v1.1)

Bootcamp III — Fase 1 (contrato) e Fase 2 (implementação).
Versão 1.0 elaborada em 08/09/2026; v1.1 inclui os alinhamentos da seção 5.

## 1. Propósito
Camada analítica que recebe uma coleção de tarefas já existente e devolve métricas de desempenho e cumprimento de prazos. Não cria, edita ou exclui tarefas.

## 2. Entrada
Lista de tarefas; cada tarefa tem:
- `id_tarefa`: inteiro positivo, único.
- `titulo`: texto não vazio, máximo 200 caracteres.
- `prioridade`: `baixa`, `média` ou `alta`.
- `status`: `concluída`, `pendente` ou `cancelada`.
- `data_criacao`: datetime em UTC, obrigatório.
- `data_inicio`: datetime em UTC, opcional.
- `data_conclusao`: datetime em UTC, obrigatório apenas quando `status` é `concluída`.
- `prazo`: datetime em UTC, obrigatório.

## 3. Saída
- `tempo_medio_conclusao_min`: média (minutos) de `data_conclusao - data_inicio` das tarefas concluídas.
- `taxa_atraso_percentual`: % de tarefas concluídas após o `prazo`, sobre o total de concluídas.
- `quantidade_tarefas`: total de tarefas efetivamente analisadas.
- `indicadores_por_prioridade`: as métricas acima recalculadas para `baixa`, `média` e `alta`.

## 4. Regras de negócio
- Só tarefas `concluída` entram no tempo médio de conclusão.
- Tarefa concluída está em atraso se `data_conclusao > prazo`.
- Tarefas `cancelada` são excluídas de qualquer cálculo.
- Sem tarefas concluídas: não há divisão por zero; retorna resultado neutro.
- Todas as datas em UTC.

## 5. Alinhamentos da v1.1 (conflitos resolvidos para a Fase 2)
1. A saída também inclui `total_tarefas`, `total_concluidas`, `total_pendentes` e `tempo_medio_conclusao_horas` (= minutos / 60), conforme o enunciado da Fase 2. `total_tarefas` = `quantidade_tarefas` = tarefas não canceladas.
2. Lote vazio, sem concluídas ou só com pendentes retorna `0.0` nas médias e taxas, sem exceção (o enunciado da Fase 2 prevalece sobre a frase do Cenário 2).
3. Se `data_inicio` não for informada, usa-se `data_criacao` como início do cálculo.
4. `TaskValidationError` é lançada para: `data_conclusao` anterior a `data_inicio` ou a `data_criacao`, campo obrigatório ausente ou inválido, valores fora do domínio e datas sem fuso (naive).

## 6. Cenários de aceite
**Cenário 1 — Sucesso.** Dado um conjunto de tarefas válidas com prioridades, prazos e status variados, quando o TaskAnalyzer é executado, então retorna tempo médio, taxa de atraso e indicadores por prioridade consistentes com os dados.

**Cenário 2 — Entradas inválidas.** Dado um conjunto com inconsistências (ex.: conclusão anterior ao início), quando o analisador é executado, então lança `TaskValidationError` com mensagem clara.

**Casos de borda.** Lote vazio ou só com pendentes retorna `0.0` nas médias, sem exceção.