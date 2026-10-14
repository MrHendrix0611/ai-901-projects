// OCR: escapar conteúdo do documento para evitar injeção HTML/XSS.
function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, char => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[char]));
}

document.getElementById('dropZone').addEventListener('click', () => document.getElementById('imageInput').click());
document.getElementById('dropZone').addEventListener('dragover', e => { e.preventDefault(); e.currentTarget.classList.add('dragover'); });
document.getElementById('dropZone').addEventListener('dragleave', e => e.currentTarget.classList.remove('dragover'));
document.getElementById('dropZone').addEventListener('drop', e => {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) {
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        document.getElementById('imageInput').files = dataTransfer.files;
        handleFile(file);
    }
});
document.getElementById('imageInput').addEventListener('change', e => { if (e.target.files[0]) handleFile(e.target.files[0]); });

function handleFile(file) {
    if (!file.type.match(/image\/(png|jpeg|jpg|bmp|tiff)/)) {
        document.getElementById('error').textContent = 'Formato inválido';
        document.getElementById('error').style.display = 'block';
        return;
    }
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('error').style.display = 'none';
    const reader = new FileReader();
    reader.onload = e => { document.getElementById('preview').src = e.target.result; document.getElementById('preview').classList.remove('preview-img'); };
    reader.readAsDataURL(file);
}

document.getElementById('uploadForm').addEventListener('submit', async e => {
    e.preventDefault();
    const input = document.getElementById('imageInput');
    if (!input.files[0]) { document.getElementById('error').textContent = 'Selecione uma imagem'; document.getElementById('error').style.display = 'block'; return; }
    document.getElementById('loading').style.display = 'block';
    document.getElementById('analyzeBtn').disabled = true;
    document.getElementById('error').style.display = 'none';
    
    const formData = new FormData();
    formData.append('image', input.files[0]);
    
    try {
        const res = await fetch('/api/analyze', { method: 'POST', body: formData });
        const data = await res.json();
        if (!data.success) { document.getElementById('error').textContent = data.error || 'Erro'; document.getElementById('error').style.display = 'block'; }
        else { renderResults(data); document.getElementById('results').style.display = 'block'; document.getElementById('demoNotice').style.display = data.demo ? 'block' : 'none'; }
    } catch (err) { document.getElementById('error').textContent = 'Erro de rede'; document.getElementById('error').style.display = 'block'; }
    finally { document.getElementById('loading').style.display = 'none'; document.getElementById('analyzeBtn').disabled = false; }
});

function renderResults(data) {
    document.getElementById('contentArea').innerHTML = '<h3>Texto Completo</h3><p>' + escapeHtml(data.content || 'N/A').replace(/\n/g, '<br>') + '</p>';
    
    let pagesHtml = '<h3>Páginas</h3>';
    if (data.pages && data.pages.length) {
        data.pages.forEach(p => {
            pagesHtml += '<div class="line-item"><strong>Página ' + escapeHtml(p.page_number) + '</strong> — ' + escapeHtml(p.width) + ' x ' + escapeHtml(p.height) + ' ' + escapeHtml(p.unit) + '</div>';
        });
    }
    document.getElementById('pagesArea').innerHTML = pagesHtml;
    
    let linesHtml = '<h3>Linhas</h3>';
    if (data.pages && data.pages.length) {
        data.pages.forEach(p => {
            p.lines.forEach(l => {
                linesHtml += '<div class="line-item"><strong>' + escapeHtml(l.content || '') + '</strong><br>Bounding box: ' + escapeHtml(JSON.stringify(l.bounding_box)) + '</div>';
            });
        });
    }
    document.getElementById('linesArea').innerHTML = linesHtml;
    
    let wordsHtml = '<h3>Palavras</h3>';
    if (data.pages && data.pages.length) {
        data.pages.forEach(p => {
            p.words.forEach(w => {
                wordsHtml += '<div class="word-item"><strong>' + escapeHtml(w.content || '') + '</strong> — Confiança: <span class="confidence">' + Math.round((w.confidence || 0) * 100) + '%</span><br>Bounding box: ' + escapeHtml(JSON.stringify(w.bounding_box)) + '</div>';
            });
        });
    }
    document.getElementById('wordsArea').innerHTML = wordsHtml;
    
    const input = document.getElementById('imageInput');
    if (input.files[0]) {
        const reader = new FileReader();
        reader.onload = e => document.getElementById('resultImage').src = e.target.result;
        reader.readAsDataURL(input.files[0]);
    }
}