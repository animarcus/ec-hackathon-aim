// File upload handling
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');

if (dropZone) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('dragover');
    }

    function unhighlight(e) {
        dropZone.classList.remove('dragover');
    }

    dropZone.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFileSelect, false);
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

function handleFileSelect(e) {
    const files = e.target.files;
    handleFiles(files);
}

function handleFiles(files) {
    if (files.length === 0) return;
    
    const file = files[0];
    if (file.type !== 'application/pdf') {
        alert('Please upload a PDF file');
        return;
    }

    uploadFile(file);
}

function uploadFile(file) {
    const formData = new FormData();
    formData.append('cv', file);

    uploadStatus.classList.remove('d-none');
    
    fetch('/upload_cv', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/chat';
        } else {
            alert(data.error || 'Error uploading file');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error uploading file');
    })
    .finally(() => {
        uploadStatus.classList.add('d-none');
    });
}

// Chat handling
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');

if (sendButton && messageInput) {
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    messageInput.value = '';
    messageInput.disabled = true;
    sendButton.disabled = true;

    fetch('/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        addMessage(data.response, 'bot');
    })
    .catch(error => {
        console.error('Error:', error);
        addMessage('Sorry, there was an error processing your message.', 'system');
    })
    .finally(() => {
        messageInput.disabled = false;
        sendButton.disabled = false;
        messageInput.focus();
    });
}

function addMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(`${type}-message`);
    messageDiv.textContent = text;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
