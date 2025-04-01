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
    const sidebarWidth = 250; // MUST MATCH .nav-container width in CSS
    const closedPosition = '10px'; // MUST MATCH .toggle-btn left in CSS (closed state)
    const openPosition = `${sidebarWidth + 10}px`; // Position next to open sidebar
    // --- End Configuration ---

    const savedState = localStorage.getItem('sidebarState');

    // Function to move button OUTSIDE nav
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

    // Function to move button INSIDE nav (into placeholder)
    function moveButtonInside() {
        placeholder.appendChild(newChatButton); // Move button into placeholder
        newChatButton.classList.remove('state-closed');
        newChatButton.classList.add('state-open');
        newChatButton.textContent = 'New Chat'; // Change text when inside (optional)
    }

    // Main function to control sidebar state
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

    // Set initial state on load
    if (savedState === 'open') {
        // IMPORTANT: Temporarily move button inside BEFORE setting state
        // to avoid brief visual glitch if it starts outside but should be inside.
        moveButtonInside();
        setSidebarState(true);
    } else {
        // Ensure button starts outside with correct class if default is closed
        moveButtonOutside(); // Explicitly place outside on load if state is closed/null
        setSidebarState(false);
    }

    // Toggle on click
    toggleBtn.addEventListener('click', function() {
        const isCurrentlyOpen = navBar.classList.contains('visible');
        setSidebarState(!isCurrentlyOpen); // Toggle the state
    });
});