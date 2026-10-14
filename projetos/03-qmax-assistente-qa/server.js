"use strict";
require('dotenv').config();
const express = require('express');
const path = require('path');
const app = express();

app.disable('x-powered-by');
app.use(express.json({limit: '16kb'}));
app.use(express.static(path.join(__dirname, 'public')));

const PROMPT = `Você é QMax, assistente virtual de Qualidade de Software.
Oriente profissionais e estudantes sobre testes manuais e automatizados,
casos de teste, documentação de bugs, testes de APIs e melhoria contínua.
Responda em português do Brasil, de forma clara e com exemplos práticos.
Para temas fora de QA, informe sua especialidade e ofereça ajuda em QA.
Não invente que executou testes ou validou sistemas reais.`;

function demoAnswer(message) {
  const s = message.toLocaleLowerCase('pt-BR');
  if (s.includes('api') || s.includes('rest')) {
    return 'DEMONSTRAÇÃO (sem Azure): Para testar uma API REST, valide endpoint e método HTTP, status codes, headers, body, autenticação, cenários negativos e automatize os casos repetitivos no Postman ou com testes de integração.';
  }
  if (s.includes('bug') || s.includes('erro')) {
    return 'DEMONSTRAÇÃO (sem Azure): Documente título, pré-condições, passos para reproduzir, resultado esperado, resultado obtido, severidade e evidências do defeito.';
  }
  return 'DEMONSTRAÇÃO (sem Azure): Sou o QMax, assistente de QA. Posso ajudar a planejar casos de teste, revisar bugs, testar APIs e discutir estratégias de qualidade de software.';
}

async function fetchAzure(message) {
  const base = (process.env.AZURE_OPENAI_BASE_URL || '').replace(/\/+$/, '');
  const key = process.env.AZURE_OPENAI_KEY || '';
  const deployment = process.env.AZURE_OPENAI_DEPLOYMENT || '';
  if (!base.startsWith('https://') || !key || !deployment) {
    throw new Error('Configuração do Azure OpenAI ausente.');
  }
  const resp = await fetch(base + '/chat/completions', {
    method: 'POST',
    headers: {'Content-Type':'application/json', 'api-key':key},
    body: JSON.stringify({
      model: deployment,
      messages:[{role:'system',content:PROMPT},{role:'user',content:message}],
      max_completion_tokens:800
    }),
    signal: AbortSignal.timeout(30000)
  });
  if (!resp.ok) throw new Error('Azure OpenAI respondeu com erro HTTP ' + resp.status);
  const json = await resp.json();
  const text = json?.choices?.[0]?.message?.content;
  if (typeof text !== 'string' || !text.trim()) throw new Error('Resposta vazia do modelo.');
  return text;
}

app.post('/api/chat', async (req, res) => {
  const message = req.body?.message;
  if (typeof message !== 'string' || message.trim().length === 0 || message.length > 2000) {
    return res.status(400).json({error:'Digite uma mensagem entre 1 e 2000 caracteres.'});
  }
  if ((process.env.APP_MODE || 'demo').toLowerCase() !== 'azure') {
    return res.json({answer:demoAnswer(message), demo:true});
  }
  try {
    return res.json({answer:await fetchAzure(message), demo:false});
  } catch (e) {
    // Não revelar endpoint, token, request body ou stack trace para o navegador.
    console.error('Falha ao consultar o Azure OpenAI:', e.message);
    return res.status(502).json({error:'Falha ao consultar o modelo Azure. Confira a configuração no servidor.'});
  }
});

if (require.main === module) {
  const port = Number(process.env.PORT || 3000);
  app.listen(port, '127.0.0.1', () => console.log('QMax disponível em http://127.0.0.1:' + port));
}
module.exports = {app, demoAnswer};
