# Arquitetura geral

```mermaid
flowchart TB
    subgraph UX[Aplicações web]
      A[EcoPredictor - Tailwind]
      B[OCR - HTML/CSS/JS]
      C[QMax - HTML/CSS/JS]
    end
    A --> D[Flask - regressão]
    B --> E[Flask - OCR]
    C --> F[Express - chatbot]
    D --> G[Azure Machine Learning]
    E --> H[Azure AI Document Intelligence]
    F --> I[Azure OpenAI - Microsoft Foundry]
```

As três aplicações têm modo `APP_MODE=demo` por padrão. Nele, **os exemplos são simulados** e não fazem requisições ao Azure. Para chamadas verdadeiras, configure `APP_MODE=azure` e credenciais locais no respectivo `.env`. Nunca versionar tokens ou arquivos de configuração real.
