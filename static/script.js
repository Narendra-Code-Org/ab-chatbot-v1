function handleKeyPress(event) {
    if (event.key === 'Enter') {
        askQuestion();
    }
}

function appendMessage(sender, text) {
    const history = document.getElementById('chat-history');
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message');
    msgDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    
    if (sender === 'bot') {
        msgDiv.innerHTML = marked.parse(text);
    } else {
        msgDiv.textContent = text;
    }
    
    history.appendChild(msgDiv);
    history.scrollTop = history.scrollHeight;
}

function updateSources(sources) {
    const list = document.getElementById('sources-list');
    list.innerHTML = '';
    
    if (!sources || sources.length === 0) {
        list.innerHTML = '<p class="desc text-muted">No sources retrieved.</p>';
        return;
    }
    
    sources.forEach(src => {
        const div = document.createElement('div');
        div.classList.add('source-item');
        const filename = src.split('/').pop().split('\\').pop();
        div.textContent = filename;
        div.title = src;
        list.appendChild(div);
    });
}

async function askQuestion() {
    const input = document.getElementById('question-input');
    const question = input.value.trim();
    const sendBtn = document.getElementById('send-btn');
    
    if (!question) return;
    
    input.value = '';
    input.disabled = true;
    sendBtn.disabled = true;
    
    appendMessage('user', question);
    
    const history = document.getElementById('chat-history');
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('message', 'bot-message');
    loadingDiv.id = 'loading-msg';
    loadingDiv.textContent = 'Thinking...';
    history.appendChild(loadingDiv);
    history.scrollTop = history.scrollHeight;
    
    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });
        
        const data = await response.json();
        
        const loadingMsg = document.getElementById('loading-msg');
        if (loadingMsg) loadingMsg.remove();
        
        if (response.ok) {
            appendMessage('bot', data.answer);
            updateSources(data.sources);
        } else {
            appendMessage('bot', `Error: ${data.error}`);
        }
    } catch (error) {
        const loadingMsg = document.getElementById('loading-msg');
        if (loadingMsg) loadingMsg.remove();
        appendMessage('bot', 'Network error occurred while fetching the response.');
    } finally {
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

async function uploadPDF() {
    const fileInput = document.getElementById('pdf-upload');
    const statusDiv = document.getElementById('upload-status');
    const uploadBtn = document.getElementById('upload-btn');
    
    if (!fileInput.files.length) {
        statusDiv.textContent = 'Please select a file first.';
        statusDiv.className = 'error';
        return;
    }
    
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    
    statusDiv.textContent = 'Uploading and processing PDF...';
    statusDiv.className = 'loading';
    uploadBtn.disabled = true;
    fileInput.disabled = true;
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            statusDiv.textContent = data.message;
            statusDiv.className = 'success';
            fileInput.value = '';
        } else {
            statusDiv.textContent = `Error: ${data.error}`;
            statusDiv.className = 'error';
        }
    } catch (error) {
        statusDiv.textContent = 'Network error occurred during upload.';
        statusDiv.className = 'error';
    } finally {
        uploadBtn.disabled = false;
        fileInput.disabled = false;
    }
}
