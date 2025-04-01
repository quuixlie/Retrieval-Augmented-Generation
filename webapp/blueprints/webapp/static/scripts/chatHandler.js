let messageInput = document.getElementById('messageInput');


function createMessage(message, isResponse) {
    let messageDiv = document.createElement('div');
    let alignment = isResponse ? 'left' : 'right';
    messageDiv.classList.add('message', alignment);
    messageDiv.textContent = message;
    return messageDiv;
}

function scrollToBottom() {
    const chatContainer = document.querySelector('.chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

let textarea = messageInput.querySelector('textarea');
textarea.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        if (event.shiftKey) {
            // Allow new line
            event.preventDefault();
            let cursorPos = textarea.selectionStart;
            let text = textarea.value;
            textarea.value = text.substring(0, cursorPos) + "\n" + text.substring(cursorPos);
            textarea.selectionStart = textarea.selectionEnd = cursorPos + 1;
        } else {
            // Submit the form
            event.preventDefault();
            messageInput.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
        }
    }
});

messageInput.addEventListener('submit', (event) => {
    event.preventDefault();
    const inputElement = messageInput.querySelector('textarea');
    let input = inputElement.value;

    inputElement.value = '';

    if (input.length <= 0)
        return;

    // Creating the message
    const userMessage = createMessage(input, false);
    document.querySelector('.chat-container').appendChild(userMessage);
    scrollToBottom()

    const loadingSpinner = document.createElement('div');
    loadingSpinner.classList.add('loader', 'flex-self-center');

    // Loading spinner
    document.querySelector('.chat-container').appendChild(loadingSpinner);

    const formData = new FormData();
    formData.append("message", input);

    const chatUrl = messageInput.getAttribute('action');
    fetch(chatUrl, {
        method: "POST",
        body: formData
    }).then(async (response) => {
        return response.json()
    }).then((data) => {

        if (data["rag_response"]) {
            // Creating the response
            const ragMessage = createMessage(data["rag_response"], true);
            document.querySelector('.chat-container').appendChild(ragMessage);

        } else if (data["error"]) {
            const errorMessage = document.createElement('div');
            errorMessage.textContent = data["error"];
            errorMessage.classList.add('rounded-corners', 'pad-16', 'bg-error', 'flex-self-center');
            document.querySelector('.chat-container').appendChild(errorMessage);
        }
        scrollToBottom()


    }).catch((error) => {
        userMessage.remove()
    }).finally(() => {
        // Removing the loading spinner
        loadingSpinner.remove();
    });
})
