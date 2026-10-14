# Segurança e privacidade

Este repositório contém **apenas configurações exemplificativas** e nenhum segredo necessário para executar os projetos.

1. **Regere/revogue imediatamente** qualquer chave que já esteve nos ZIPs originais (Azure Machine Learning, Document Intelligence e Azure OpenAI), mesmo que os projetos nunca tenham sido publicados.
2. Crie seu `.env` local a partir de `.env.example`; nunca envie o `.env` ao GitHub.
3. Configure as chaves apenas no backend. Não exponha chaves em `public/`, `.js`, prints, logs ou URLs.
4. Não publique uploads, contratos, notas fiscais reais ou documentos com dados pessoais.
5. Antes de cada `git push`, revise `git diff --cached`, rode `python scripts/check_secrets.py` e verifique `git status --ignored`.
6. Para uso público/produção: implemente autenticação, limitação de chamadas, monitoramento de gastos e política de retenção.

Se um segredo foi commitado, **apagá-lo no commit seguinte não basta**: revogue a credencial, e caso necessário trate o histórico Git e a exposição junto ao proprietário da assinatura.

Mockups de interface em `docs/mockups/` são **imagens ilustrativas, não evidências de inferência real**.
