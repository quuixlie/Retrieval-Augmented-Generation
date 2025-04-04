document.addEventListener('DOMContentLoaded', function () {
    const sidebarButtons = document.getElementById("sidebarButtonsContainer");
    const toggleBtn = document.getElementById('toggleNav');
    const navBar = document.getElementById('navBar');

    const savedState = localStorage.getItem('sidebarState');
    if (savedState === 'open') {
        navBar.classList.add('visible');
        toggleBtn.textContent = '‹';
    } else {
        toggleBtn.textContent = '›';
    }

    toggleBtn.addEventListener('click', function () {
        const isOpening = !navBar.classList.contains('visible');

        navBar.classList.toggle('visible');

        if (isOpening) {
            toggleBtn.textContent = '‹';
            localStorage.setItem('sidebarState', 'open');
        } else {
            toggleBtn.textContent = '›';
            localStorage.setItem('sidebarState', 'closed');
        }
    });


});


// Context menu

let contextMenu = null;
let activeConversationID = null;

document.addEventListener("DOMContentLoaded", () => {
    contextMenu = document.getElementById("conversationContextMenu")
})

function showMenu(x, y) {
    if (contextMenu) {
        contextMenu.style.display = "block";
        contextMenu.style.top = `${y}px`;
        contextMenu.style.left = `${x}px`;
    }
}

function hideMenu() {
    if (contextMenu) {
        contextMenu.style.display = "none";
    }
}

function toggleMenu(event) {
    event.stopPropagation()


    const activeButton = event.target.closest("button");
    const rect = activeButton.getBoundingClientRect();

    console.log(activeButton)

    activeConversationID = activeButton.getAttribute("data-conversation-id")


    showMenu(rect.x, rect.y);
}

function deleteConversation() {
    if (activeConversationID) {
        console.log(`Deleting conversation ${activeConversationID}`);
    }
    hideMenu()
}

