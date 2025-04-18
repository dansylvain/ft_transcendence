if (typeof themeToggle === 'undefined') {
    let themeToggle = document.querySelector('.switch .input');

    if (themeToggle) {
        const htmlEl = document.documentElement;
        themeToggle.addEventListener('change', () => {
            if (themeToggle.checked) {
                htmlEl.setAttribute('data-theme', 'dark');
            } else {
                htmlEl.setAttribute('data-theme', 'light');
            }
        });
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            htmlEl.setAttribute('data-theme', savedTheme);
            themeToggle.checked = savedTheme === 'dark';
        }

        themeToggle.addEventListener('change', () => {
            const newTheme = themeToggle.checked ? 'dark' : 'light';
            htmlEl.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
}
