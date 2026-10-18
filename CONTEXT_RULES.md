# CONTEXT_RULES — TaskAnalyzer

Regras persistentes para o assistente de IA. Fornecer este arquivo e `specs/task_analyzer_spec.md` antes de qualquer solicitação de código.

## 1. Diretrizes arquiteturais obrigatórias
- Python 3.11 ou superior.
- Type hints em todas as funções, métodos e parâmetros.
- Princípio de responsabilidade única; funções pequenas, coesas e com um único propósito.
- Estilo PEP 8; docstrings no padrão Google em módulos, classes e funções.
- Exceções específicas, com mensagens claras.
- Eventos relevantes registrados com o módulo padrão `logging`.
- Nomes de variáveis e funções que expressem sua finalidade.

## 2. Proibições explícitas
- Não usar bibliotecas externas além da biblioteca padrão do Python (e pytest para testes).
- Não alterar, remover ou adaptar os cenários de aceite.
- Não modificar a estrutura de pastas do repositório.
- Não persistir dados em arquivos ou bancos de dados (apenas em memória).
- Não alterar a assinatura das funções públicas sem autorização explícita.
- Não entregar funcionalidade nova sem testes automatizados correspondentes.
- Não duplicar código desnecessariamente.
- Não assumir comportamentos que não estejam especificados no contrato.

## 3. Regras de interação com a IA
- Fornecer sempre o contexto completo (spec + CONTEXT_RULES) antes de pedir código.
- Pedir à IA um resumo do entendimento do contrato antes de avançar.
- Em caso de dúvida sobre a solução, pedir explicação.
- Todo código gerado passa por revisão crítica humana antes de ser aceito.
- Respostas que violem qualquer regra acima são rejeitadas e corrigidas antes de prosseguir.