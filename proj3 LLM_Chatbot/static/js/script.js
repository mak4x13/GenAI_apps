document.addEventListener('DOMContentLoaded', () => {
    const messagesContainer = document.getElementById('messages-container');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const addMessage = (message, role) => {
        const messageWrapper = document.createElement('div');
        messageWrapper.className = `message ${role}`;

        const avatar = document.createElement('img');
        // Correct paths for Flask's static folder serving
        avatar.src = (role === 'user') ? '/static/user.jpg' : '/static/Bot_logo.png';
        avatar.alt = `${role} avatar`;
        
        if (role === 'error') {
            avatar.src = '/static/Bot_logo.png'; // Use bot logo for errors too
        }

        const messageBubble = document.createElement('p');
        messageBubble.innerText = message;

        messageWrapper.appendChild(avatar);
        messageWrapper.appendChild(messageBubble);
        messagesContainer.appendChild(messageWrapper);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    };
    
    const showLoadingIndicator = () => {
        const loadingElement = document.createElement('div');
        loadingElement.className = 'message aibot loading-animation';
        loadingElement.innerHTML = `
            <img src="/static/Bot_logo.png" alt="bot avatar">
            <div class="loading-dots">
                <div class="dot1"></div>
                <div class="dot2"></div>
                <div class="dot3"></div>
            </div>
        `;
        messagesContainer.appendChild(loadingElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    };

    const removeLoadingIndicator = () => {
        const loadingElement = document.querySelector('.loading-animation');
        if (loadingElement) {
            loadingElement.remove();
        }
    };

    const sendMessage = async (message) => {
        addMessage(message, 'user');
        showLoadingIndicator();

        try {
            const response = await fetch('http://192.168.1.2:5000/chatbot', { // set this to pc IP for accessing on mobile or other devices
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                         prompt: message,
                        session_id: sessionId
                    })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.text();
            removeLoadingIndicator();
            addMessage(data, 'aibot');

        } catch (error) {
            console.error('Error:', error);
            removeLoadingIndicator();
            addMessage(`Sorry, something went wrong. Please check the console for details.`, 'error');
        }
    };

    messageForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const message = messageInput.value.trim();
        if (message) {
            messageInput.value = '';
            await sendMessage(message);
        }
    });

    messageInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            messageForm.dispatchEvent(new Event('submit', { cancelable: true }));
        }
    });
    
});