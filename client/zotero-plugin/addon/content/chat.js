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

    try {
        // Send request to your local API Gateway
        const response = await fetch('http://localhost:8000/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: question,
                limit: 5
            })
        });

        if (!response.ok) throw new Error("Gateway Error");

        const data = await response.json();

        // Remove loading indicator
        document.getElementById(loadingId).remove();

        // Check how many chunks the vector DB found
        const chunkCount = data.context ? data.context.length : 0;
        history.innerHTML += `<div class="message bot-msg"><b>Assistant:</b> Connection successful! Retrieved ${chunkCount} relevant text chunks from the vector database. (LLM not connected yet)</div>`;

    } catch (error) {
        document.getElementById(loadingId).remove();
        history.innerHTML += `<div class="message error-msg"><b>Error:</b> Could not connect to the backend API Gateway. Is the Python server running on port 8000?</div>`;
    }
    
    history.scrollTop = history.scrollHeight;
});

// Allow hitting "Enter" to send the message
document.getElementById('question').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        document.getElementById('ask-btn').click();
    }
});
