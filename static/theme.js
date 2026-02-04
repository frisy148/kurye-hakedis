(() => {
    const storageKey = 'kurye-theme';
    const root = document.documentElement;

    const getPreferredTheme = () => {
        const stored = localStorage.getItem(storageKey);
        if (stored === 'light' || stored === 'dark') {
            return stored;
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };

    const updateToggleLabels = (theme) => {
        document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
            const isDark = theme === 'dark';
            btn.setAttribute('aria-pressed', String(isDark));
            const labelEl = btn.querySelector('[data-theme-text]');
            if (labelEl) {
                labelEl.textContent = isDark ? 'Açık Mod' : 'Dark Mod';
            }
        });
    };

    const applyTheme = (theme) => {
        root.setAttribute('data-theme', theme);
        document.body.classList.toggle('theme-dark', theme === 'dark');
        updateToggleLabels(theme);
    };

    const toggleTheme = () => {
        const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        applyTheme(next);
        localStorage.setItem(storageKey, next);
    };

    const init = () => {
        applyTheme(getPreferredTheme());

        document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
            if (btn.dataset.themeBound === 'true') {
                return;
            }
            btn.dataset.themeBound = 'true';
            btn.addEventListener('click', toggleTheme);
        });
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
