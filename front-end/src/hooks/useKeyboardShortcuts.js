import { useEffect } from 'react';

/**
 * Keyboard Shortcuts Hook
 * Implements global keyboard shortcuts:
 * - g+h: Go to home
 * - g+a: Go to admin (if admin)
 * - s: Focus search
 * - ?: Show help
 */
const useKeyboardShortcuts = (navigate, user) => {
  useEffect(() => {
    let gPressed = false;
    let gTimeout;

    const handleKeyDown = (e) => {
      // Check if user is typing in an input/textarea
      if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
        if (e.key !== 'Escape') return;
      }

      // Handle 'g' key (for combinations)
      if (e.key === 'g' && !gPressed) {
        gPressed = true;
        gTimeout = setTimeout(() => {
          gPressed = false;
        }, 1000);
        return;
      }

      // g+h: Go home
      if (e.key === 'h' && gPressed) {
        e.preventDefault();
        gPressed = false;
        clearTimeout(gTimeout);
        navigate('/');
      }

      // g+a: Go to admin (if admin)
      if (e.key === 'a' && gPressed && user?.role === 'admin') {
        e.preventDefault();
        gPressed = false;
        clearTimeout(gTimeout);
        navigate('/admin');
      }

      // s: Focus search
      if (e.key === 's' && !gPressed) {
        e.preventDefault();
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
          searchInput.focus();
        }
      }

      // ?: Show help
      if (e.key === '?' && !e.shiftKey) {
        e.preventDefault();
        showKeyboardHelp();
      }

      // Escape: Close modals/menus
      if (e.key === 'Escape') {
        // Close any open dropdowns
        document.querySelectorAll('.user-dropdown-menu, .view-switcher-menu').forEach((el) => {
          el.style.display = 'none';
        });
      }
    };

    const showKeyboardHelp = () => {
      const helpText = `
Keyboard Shortcuts:
- g + h: Go to home
${user?.role === 'admin' ? '- g + a: Go to admin console\n' : ''}- s: Focus search bar
- ?: Show this help
- Esc: Close menus/modals
      `;
      alert(helpText.trim());
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      clearTimeout(gTimeout);
    };
  }, [navigate, user]);
};

export default useKeyboardShortcuts;
