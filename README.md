# sdd-taskanalyzer

Módulo TaskAnalyzer desenvolvido com Spec-Driven Development e assistente de IA (Bootcamp III, Fase 2).

## Executar
    pip install -r requirements.txt
    python -m pytest -v

## Estrutura
- `specs/task_analyzer_spec.md`: contrato SDD
- `CONTEXT_RULES.md`: regras de governança para a IA
- `src/task_analyzer.py`: implementação (`analyze_tasks`, `TaskValidationError`)
- `tests/test_harness.py`: testes com pytest

## Status
13 testes passando (pytest).