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


// Uploading files

document.addEventListener('DOMContentLoaded', () => {
    const documentInput = document.getElementById("documentInput")

    documentInput.addEventListener("change", () => {
        const files = documentInput.files
        const url = documentInput.getAttribute('data-url')
        console.log(`URL : ${url}`)

        if (!files || files.length <= 0) {
            console.log("no files provided")
            return;
        }

        if (!url) {
            console.log("no url provided")
            return;
        }


        console.log(`files : ${files}`)
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append("files", files[i])
        }

        console.log([...formData])

        fetch(url, {
            method: "POST",
            body: formData
        }).then(async (response) => {
            if (!response.ok) {
                const json = await response.json()

                if (json["error"]) {
                    console.log(`Server error: ${json["error"]}`)
                } else {
                    console.log("unkonwn reror")
                }
            }
            console.log("Success")
        }).catch((error) => {
            console.log("Coulnd't upload files")

        });

    })
})
