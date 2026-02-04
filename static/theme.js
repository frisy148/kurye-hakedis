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

    const syncThemeToggles = (theme) => {
        document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
            const isDark = theme === 'dark';
            btn.setAttribute('aria-pressed', String(isDark));
            btn.classList.toggle('is-dark', isDark);
        });
    };

    const applyTheme = (theme) => {
        root.setAttribute('data-theme', theme);
        document.body.classList.toggle('theme-dark', theme === 'dark');
        syncThemeToggles(theme);
    };

    const toggleTheme = () => {
        const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        applyTheme(next);
        localStorage.setItem(storageKey, next);
    };

    const registerThemeToggleHandlers = () => {
        document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
            if (btn.dataset.themeBound === 'true') {
                return;
            }
            btn.dataset.themeBound = 'true';
            btn.addEventListener('click', toggleTheme);
        });
    };

    const setSectionExpanded = (button, expanded) => {
        button.setAttribute('aria-expanded', String(expanded));
        const icon = button.querySelector('[data-toggle-icon]');
        if (icon) {
            icon.textContent = expanded ? '−' : '+';
        }
        const section = button.closest('.details-section');
        if (section) {
            section.classList.toggle('is-collapsed', !expanded);
            const content = section.querySelector('[data-section-content]');
            if (content) {
                content.hidden = !expanded;
            }
        }
    };

    const registerSectionToggles = () => {
        document.querySelectorAll('[data-section-toggle]').forEach((btn) => {
            if (btn.dataset.sectionBound === 'true') {
                return;
            }
            btn.dataset.sectionBound = 'true';
            btn.addEventListener('click', () => {
                const expanded = btn.getAttribute('aria-expanded') !== 'false';
                const nextExpanded = !expanded;
                setSectionExpanded(btn, nextExpanded);
            });
            setSectionExpanded(btn, btn.getAttribute('aria-expanded') !== 'false');
        });
    };

    const init = () => {
        applyTheme(getPreferredTheme());
        registerThemeToggleHandlers();
        registerSectionToggles();
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
