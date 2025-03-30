document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('toggleNav');
    const navBar = document.getElementById('navBar');

    const savedState = localStorage.getItem('sidebarState');
    if (savedState === 'open') {
        navBar.classList.add('visible');
        toggleBtn.textContent = '‹';
        toggleBtn.style.left = '140px';
    } else {
        toggleBtn.textContent = '›';
    }

    toggleBtn.addEventListener('click', function() {
        const isOpening = !navBar.classList.contains('visible');

        navBar.classList.toggle('visible');

        if (isOpening) {
            toggleBtn.textContent = '‹';
            toggleBtn.style.left = '140px';
            localStorage.setItem('sidebarState', 'open');
        } else {
            toggleBtn.textContent = '›';
            // toggleBtn.textContent = '‹';
            toggleBtn.style.left = '20px';
            localStorage.setItem('sidebarState', 'closed');
        }
    });
});
