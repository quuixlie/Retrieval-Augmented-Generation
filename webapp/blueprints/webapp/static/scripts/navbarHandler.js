document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('toggleNav');
    const navBar = document.getElementById('navBar');
    const body = document.body;
    const newChatButton = document.getElementById('newChatButton');
    const placeholder = document.getElementById('newChatButtonPlaceholder');
    // Store the original container where the button sits when closed
    // This assumes the button is placed directly after navBar in the HTML body/container
    const buttonOriginalContainer = navBar.parentNode;
    const buttonNextSibling = navBar.nextSibling; // Element after navBar (or null)

    // --- Configuration ---
    const sidebarWidth = 300; // MUST MATCH .nav-container width in CSS
    const closedPosition = '10px'; // MUST MATCH .toggle-btn left in CSS (closed state)
    const openPosition = `${sidebarWidth + 10}px`; // Position next to open sidebar


    const savedState = localStorage.getItem('sidebarState');

    function moveButtonOutside() {
        // Insert the button back into its original spot outside the nav
        // Checks if there was an element after navBar to insert before, otherwise appends
        if (buttonNextSibling) {
             buttonOriginalContainer.insertBefore(newChatButton, buttonNextSibling);
        } else {
             buttonOriginalContainer.appendChild(newChatButton);
        }
        newChatButton.classList.remove('state-open');
        newChatButton.classList.add('state-closed');
        newChatButton.textContent = '+'; // Ensure correct text/icon
    }

    function moveButtonInside() {
        placeholder.appendChild(newChatButton); // Move button into placeholder
        newChatButton.classList.remove('state-closed');
        newChatButton.classList.add('state-open');
        // newChatButton.textContent = 'New Chat'; // Change text when inside (optional)
    }


    function setSidebarState(isOpen) {
        if (isOpen) {
            navBar.classList.add('visible');
            body.classList.add('sidebar-open');
            toggleBtn.textContent = '‹';
            toggleBtn.style.left = openPosition;
            moveButtonInside(); // Move button INTO sidebar
            localStorage.setItem('sidebarState', 'open');
        } else {
            navBar.classList.remove('visible');
            body.classList.remove('sidebar-open');
            toggleBtn.textContent = '›';
            toggleBtn.style.left = closedPosition;
            moveButtonOutside(); // Move button OUT of sidebar
            localStorage.setItem('sidebarState', 'closed');
        }
    }

    if (savedState === 'open') {
        moveButtonInside();
        setSidebarState(true);
    } else {
        moveButtonOutside();
        setSidebarState(false);
    }

    toggleBtn.addEventListener('click', function() {
        const isCurrentlyOpen = navBar.classList.contains('visible');
        setSidebarState(!isCurrentlyOpen); // Toggle the state
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

