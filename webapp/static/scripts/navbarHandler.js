document.addEventListener('DOMContentLoaded', function () {
    const toggleNavCheckbox = document.getElementById('toggleNav');
    const newChatButton = document.getElementById('newChatButton');

    const insideButtonsContainer = document.getElementById('insideButtonsContainer');
    const outsideButtonsContainer = document.getElementById('outsideButtonsContainer');

    const savedState = localStorage.getItem('sidebarState');

    function moveButtonOutside() {
        newChatButton.remove()
        outsideButtonsContainer.appendChild(newChatButton);
    }

    function moveButtonInside() {
        newChatButton.remove()
        insideButtonsContainer.appendChild(newChatButton);
    }


    function setSidebarState(isOpen) {
        if (isOpen) {
            moveButtonInside();
            localStorage.setItem('sidebarState', 'open');
        } else {
            moveButtonOutside();
            localStorage.setItem('sidebarState', 'closed');
        }
    }

    if (savedState === 'open') {
        toggleNavCheckbox.checked = true;
        setSidebarState(true);
    } else {
        toggleNavCheckbox.checked = false;
        setSidebarState(false);
    }

    toggleNavCheckbox.addEventListener('change', function () {
        const isOpen = toggleNavCheckbox.checked;
        setSidebarState(isOpen);
    });
    newChatButton.addEventListener('click', function (e) {
        e.preventDefault()
        const link = e.target.href;
        setSidebarState(true)
        window.location.href = link;
    })
});


// Context menu

let contextMenu = null;
let selectedButton = null;
let selectedConversationId = null;

document.addEventListener("DOMContentLoaded", () => {
    contextMenu = document.getElementById("conversationContextMenu")
    // Hiding menu when user clicks somewhere
    document.addEventListener("click", hideMenu);
})

function showMenu(x, y) {
    if (contextMenu) {
        contextMenu.style.display = "block";
        contextMenu.style.top = `${y}px`;
        contextMenu.style.left = `${x}px`;
    } else {
        console.error("Context menu not found");
    }
}

function hideMenu() {
    if (contextMenu) {
        contextMenu.style.display = "none";
    } else {
        console.error("Context menu not found");
    }
    selectedButton = null;
    selectedConversationId = null;
}

function toggleMenu(event) {
    event.stopPropagation()

    selectedButton = event.target.closest("button");
    const rect = selectedButton.getBoundingClientRect();

    console.log(selectedButton)

    selectedConversationId = selectedButton.getAttribute("data-conversation-id")

    showMenu(rect.x, rect.y);
}

function deleteConversation(deleteURL, current_conv_id, redirectURL) {
    if (!selectedConversationId) {
        console.error("No active conversation ID")
        return
    }
    const listentry = selectedButton.closest('li');

    const url = `${deleteURL.slice(0, deleteURL.lastIndexOf("/"))}/${selectedConversationId}`
    console.log(url)

    fetch(url, {
        method: "DELETE",
    }).then((response) => {
        if (response.ok) {
            listentry.remove()

            if (current_conv_id == selectedConversationId) {
                window.location.replace(redirectURL)
            }

            hideMenu()
            console.log("Conversation deleted successfully")

        } else {
            console.error("Error deleting conversation")
        }
    }).catch((error) => {
        console.error("Error deleting conversation", error)
    });

}

