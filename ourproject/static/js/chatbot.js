document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const chatBody = document.getElementById('chatBody');

    // Function to display chat messages
    function appendMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        const messagePara = document.createElement('p');
        messagePara.textContent = text;
        messageDiv.appendChild(messagePara);
        chatBody.appendChild(messageDiv);
        chatBody.scrollTop = chatBody.scrollHeight; // Scroll to bottom
    }

    // Listen for form submission
    chatForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;

        appendMessage(text, 'user'); // Show user's message
        userInput.value = '';

        fetch('/dialogflow', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: text })
        })
        .then(response => response.json())
        .then(data => {
            appendMessage(data.reply, 'bot'); // Show bot's response
        })
        .catch(error => {
            console.error('Error:', error);
            appendMessage('Sorry, something went wrong.', 'bot');
        });
    });
});
