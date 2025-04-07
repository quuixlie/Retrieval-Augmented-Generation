document.addEventListener('DOMContentLoaded', () => {

    const documentInput = document.getElementById("documentInput")
    const messageInput = document.getElementById('messageInput');

    // Creating the spinner
    const loader = document.createElement('div');
    const spinner = document.createElement('div');
    loader.style.transition = "all 0.5s ease-in-out";
    loader.appendChild(spinner);
    loader.classList.add("flex-col", "flex-content-center", "shrink", "flex-self-center")
    loader.style.display = "none"
    spinner.classList.add('loader');

    // height of .loader class
    document.querySelector('.chat-container').appendChild(loader);

    function showLoadingSpinner() {

        loader.remove();
        document.querySelector('.chat-container').appendChild(loader);

        loader.classList.replace('shrink', 'expand');

        loader.style.display = "block";
        loader.style.marginBottom = "100px";
        loader.style.marginTop = "50px";
    }

    function hideLoadingSpinner() {
        loader.classList.replace('expand', 'shrink');
        loader.style.marginBottom = "0px";
        loader.style.marginTop = "0px";

        loader.remove();
        document.querySelector('.chat-container').appendChild(loader);
    }

    // Disables the buttons that could be in conflict
    function lockChat() {
        showLoadingSpinner()
        scrollToBottom()
        documentInput.disabled = true;
        messageInput.disabled = true;
        for (let c of messageInput.children) {
            c.disabled = true;
        }
    }

    function unlockChat() {
        hideLoadingSpinner()
        scrollToBottom()
        documentInput.disabled = false;
        messageInput.disabled = false;
        for (let c of messageInput.children) {
            c.disabled = false;
        }
    }

    function createMessage(message, isResponse) {
        let messageDiv = document.createElement('div');
        let alignment = isResponse ? 'left' : 'right';
        messageDiv.classList.add('message', alignment);
        messageDiv.innerText = message;
        return messageDiv;
    }

    function addMessageToChat(message) {


        let container = document.querySelector('.chat-container');
        container.appendChild(message);

        loader.remove()
        document.querySelector('.chat-container').appendChild(loader);
    }

    function chatError(errorMessage) {
        const errorElement = document.createElement('div');
        errorElement.textContent = errorMessage;
        errorElement.classList.add('rounded-corners', 'pad-16', 'bg-error', 'flex-self-center');
        addMessageToChat(errorElement);
    }

    function chatInfo(infoMessage) {
        const infoElement = document.createElement('div');
        infoElement.textContent = infoMessage;
        infoElement.classList.add('rounded-corners', 'pad-16', 'bg-info', 'flex-self-center');
        addMessageToChat(infoElement);
    }

    function scrollToBottom() {
        const chatContainer = document.querySelector('.chat-container');
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }


    scrollToBottom()

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
        addMessageToChat(userMessage);
        scrollToBottom()

        lockChat()

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
                addMessageToChat(ragMessage);
            } else if (data["error"]) {
                chatError(data["error"])
            }


        }).catch((error) => {
            userMessage.remove()
        }).finally(() => {
            // Removing the loading spinner
            scrollToBottom()
            unlockChat()
        });
    })


// Uploading files

    function refreshFileList(newHTML) {
        const fileList = document.getElementById("documentList")
        const template = document.createElement('template');
        template.innerHTML = newHTML.trim();
        const newFileList = template.content.firstChild;
        fileList.replaceWith(newFileList);
    }

    documentInput.addEventListener("change", () => {
        const files = documentInput.files
        const url = documentInput.getAttribute('data-url')

        if (!files || files.length <= 0) {
            chatError("No files selected")
            console.error("Selected files: " + files)
            scrollToBottom()
            return;
        }

        if (!url) {
            chatError("No URL provided for file upload")
            console.error("File upload url: " + url)
            scrollToBottom()
            return;
        }

        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append("files", files[i])
        }

        lockChat()

        fetch(url, {
            method: "POST",
            body: formData
        }).then(async (response) => {
            if (response.ok) {
                refreshFileList(await response.text());
                chatInfo("Files uploaded successfully")

            } else {
                const json = await response.json()
                if (json["error"]) {
                    console.error(`Server error: ${json["error"]}`)
                } else {
                    console.error("Unknown error")
                    throw new Error("Unknown error")
                }
            }
        }).catch((error) => {
            console.log("Couldn't upload files", error)
        }).finally(
            () => {
                scrollToBottom()
                unlockChat()
            }
        );

    })
})
