document.addEventListener('DOMContentLoaded', () => {
    const questionInput = document.getElementById('question');
    const askButton = document.getElementById('ask-button');

    // Listen for Enter key press on the input field
    questionInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();  // Prevent the default form submission
            askButton.click();  // Trigger the ask button click
        }
    });
});

async function askQuestion() {
    const questionInput = document.getElementById('question');
    const question = questionInput.value.trim();
    if (!question) return;

    const responseDiv = document.getElementById('response');

    // Make the response section visible after the first question
    if (responseDiv.classList.contains('hidden')) {
        responseDiv.classList.remove('hidden');
    }

    responseDiv.innerHTML += `<div class="message user-question"><strong>You:</strong> ${question}</div>`;

    const response = await fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question })
    });

    const data = await response.json();
    responseDiv.innerHTML += `<div class="message bot-response"><strong>AI:</strong> ${data.answer}</div>`;
    responseDiv.scrollTop = responseDiv.scrollHeight;  // Auto-scroll to the latest message
    questionInput.value = '';

    if (data.success) {
        alert(`Correct! You guessed it in ${data.time_taken} seconds and ${data.question_count} questions.`);
        location.reload();  // Reload to start a new game
    }
}
