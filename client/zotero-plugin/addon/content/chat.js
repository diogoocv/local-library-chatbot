window.onload = () => {
    window.focus();
    document.getElementById('api-key').focus();
};

document.getElementById('ask-btn').addEventListener('click', async () => {
    const questionInput = document.getElementById('question');
    const question = questionInput.value.trim();
    const history = document.getElementById('chat-history');

    if (!question) return;

    // Display user question
    history.innerHTML += `<div class="message user-msg"><b>You:</b> ${question}</div>`;
    
    // Add loading indicator
    const loadingId = 'loading-' + Date.now();
    history.innerHTML += `<div class="message bot-msg" id="${loadingId}"><i>Thinking...</i></div>`;
    
    // Auto-scroll to bottom
    history.scrollTop = history.scrollHeight;
    
    // Clear input
    questionInput.value = '';
    const askBtn = document.getElementById('ask-btn');
    askBtn.disabled = true;
    questionInput.disabled = true;

    try {
        // Send request to the local API Gateway
        const apiKey = document.getElementById('api-key').value.trim();

        const response = await fetch('http://localhost:8000/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: question,
                limit: 5,
                google_api_key: apiKey // Pass the key dynamically
            })
        });

        if (!response.ok) throw new Error("Gateway Error");

        const data = await response.json();

        // Remove loading indicator
        document.getElementById(loadingId).remove();

        // Display the LLM response and the routing decision
        if (data.answer) {
            // Prints the text answer
            history.innerHTML += `<div class="message bot-msg"><b>Assistant:</b> ${data.answer}</div>`;

            // If an image URL is present, inject an image element into the chat
            if (data.image_url && !data.image_url.startsWith("Error") && !data.image_url.startsWith("Could not")) {
                history.innerHTML += `<div class="message bot-img" style="margin: 10px 0;"><img src="${data.image_url}" alt="Generated Chart" style="max-width: 100%; border-radius: 4px; border: 1px solid #ddd;"></div>`;
            } else if (data.image_url) {
                // If the tool returned an error string instead of a URL
                history.innerHTML += `<div class="message error-msg" style="font-size: 11px;"><i>[Generation Notice: ${data.image_url}]</i></div>`;
            }

            // Print the routing tag at the bottom
            history.innerHTML += `<div class="message" style="font-size: 11px; color: #888; margin-top: 5px; margin-bottom: 15px;"><i>[Routed via: ${data.pipeline_used}]</i></div>`;
        } else {
            history.innerHTML += `<div class="message error-msg"><b>Error:</b> Received malformed response from the backend router.</div>`;
        }

    } catch (error) {
        document.getElementById(loadingId).remove();
        history.innerHTML += `<div class="message error-msg"><b>Error:</b> Could not connect to the backend API Gateway. Is the Python server running on port 8000?</div>`;
    } finally {
        // Re-enable inputs and return focus to the text box
        askBtn.disabled = false;
        questionInput.disabled = false;
        questionInput.focus();
        history.scrollTop = history.scrollHeight;
    }
});

// Allow hitting "Enter" to send the message
document.getElementById('question').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        document.getElementById('ask-btn').click();
    }
});
