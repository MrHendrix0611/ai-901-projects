// O frontend NUNCA armazena chaves do Azure. A integração é feita pelo Express.
const secaoConversa = document.getElementById('conversa');
const pergunta = document.getElementById('pergunta');

function addMessageToChat(className, messageContent) {
  const div = document.createElement('div');
  div.className = 'div_card_conversa';
  div.classList.add(className);
  const p = document.createElement('p');
  p.textContent = String(messageContent || ''); // Sem innerHTML de conteúdo de usuário/IA
  p.style.whiteSpace = 'pre-wrap';
  div.appendChild(p);
  if (className === 'div_card_conversa_chat') {
    const avatar = document.createElement('img');
    avatar.src = 'bot.png';
    avatar.alt = 'Imagem do robô QMax';
    avatar.style.maxWidth = '120px';
    avatar.style.maxHeight = '120px';
    div.appendChild(avatar);
  }
  secaoConversa.appendChild(div);
  secaoConversa.scrollTop = secaoConversa.scrollHeight;
}

document.querySelector('form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = pergunta.value.trim();
  if (!message) return;
  pergunta.value = '';
  addMessageToChat('div_card_conversa_usuario', message);
  try {
    const res = await fetch('/api/chat', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message})
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Não foi possível obter resposta.');
    if (data.demo) document.getElementById('demoBanner').style.display = 'block';
    addMessageToChat('div_card_conversa_chat', data.answer);
  } catch (error) {
    addMessageToChat('div_card_conversa_chat', `Erro: ${error.message}`);
  }
});
