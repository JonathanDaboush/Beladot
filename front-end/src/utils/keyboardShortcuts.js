/**
 * Keyboard Shortcuts Hook
 * Global keyboard shortcuts for power users
 * Usage: useKeyboardShortcuts(shortcuts)
 */
import { useEffect } from 'react';

// Keyboard shortcut definitions by role
export const SHORTCUTS = {
  // Global shortcuts (all roles)
  GLOBAL: {
    SEARCH: { key: '/', ctrlKey: false, description: 'Focus search' },
    HELP: { key: '?', shiftKey: true, description: 'Show keyboard shortcuts' },
    ESCAPE: { key: 'Escape', description: 'Close modals/cancel' },
  },

  // Customer shortcuts
  CUSTOMER: {
    VIEW_CART: { key: 'c', ctrlKey: true, description: 'View cart' },
    CHECKOUT: { key: 'h', ctrlKey: true, description: 'Go to checkout' },
    MY_ORDERS: { key: 'o', ctrlKey: true, description: 'View my orders' },
  },

  // Seller shortcuts
  SELLER: {
    NEW_PRODUCT: { key: 'n', ctrlKey: true, description: 'Add new product' },
    VIEW_ORDERS: { key: 'o', ctrlKey: true, description: 'View orders' },
    DASHBOARD: { key: 'd', ctrlKey: true, description: 'Go to dashboard' },
  },

  // Customer Service shortcuts
  CS: {
    NEW_TICKET: { key: 'n', ctrlKey: true, description: 'Create new ticket' },
    SEARCH_ORDER: { key: 'o', ctrlKey: true, description: 'Search orders' },
    SEARCH_USER: { key: 'u', ctrlKey: true, description: 'Search users' },
    NEXT_TICKET: { key: 'j', description: 'Next ticket' },
    PREV_TICKET: { key: 'k', description: 'Previous ticket' },
  },

  // Finance shortcuts
  FINANCE: {
    PAYROLL: { key: 'p', ctrlKey: true, description: 'View payroll' },
    REPORTS: { key: 'r', ctrlKey: true, description: 'View reports' },
  },

  // Transport shortcuts
  TRANSPORT: {
    SHIPMENTS: { key: 's', ctrlKey: true, description: 'View shipments' },
    SCAN_BARCODE: { key: 'b', ctrlKey: true, description: 'Scan barcode' },
  },

  // Manager shortcuts
  MANAGER: {
    APPROVALS: { key: 'a', ctrlKey: true, description: 'View approvals' },
    TEAM: { key: 't', ctrlKey: true, description: 'View team' },
    APPROVE: { key: 'y', description: 'Approve selected' },
    DENY: { key: 'n', description: 'Deny selected' },
  },

  // Admin shortcuts
  ADMIN: {
    USERS: { key: 'u', ctrlKey: true, description: 'Manage users' },
    SETTINGS: { key: ',', ctrlKey: true, description: 'System settings' },
    SWITCH_ROLE: { key: 'r', ctrlKey: true, shiftKey: true, description: 'Switch role view' },
  },
};

// Custom hook for keyboard shortcuts
export const useKeyboardShortcuts = (shortcuts, dependencies = []) => {
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Don't trigger shortcuts when typing in inputs
      if (
        event.target.tagName === 'INPUT' ||
        event.target.tagName === 'TEXTAREA' ||
        event.target.isContentEditable
      ) {
        // Exception: allow ESC in inputs
        if (event.key !== 'Escape') {
          return;
        }
      }

      shortcuts.forEach((shortcut) => {
        const { key, ctrlKey = false, shiftKey = false, altKey = false, callback } = shortcut;

        const keyMatches = event.key.toLowerCase() === key.toLowerCase();
        const ctrlMatches = event.ctrlKey === ctrlKey || event.metaKey === ctrlKey;
        const shiftMatches = event.shiftKey === shiftKey;
        const altMatches = event.altKey === altKey;

        if (keyMatches && ctrlMatches && shiftMatches && altMatches) {
          event.preventDefault();
          callback();
        }
      });
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, dependencies);
};

// Get all shortcuts for a role
export const getShortcutsForRole = (role) => {
  const roleShortcuts = {
    CUSTOMER: { ...SHORTCUTS.GLOBAL, ...SHORTCUTS.CUSTOMER },
    SELLER: { ...SHORTCUTS.GLOBAL, ...SHORTCUTS.SELLER },
    CUSTOMER_SERVICE: { ...SHORTCUTS.GLOBAL, ...SHORTCUTS.CS },
    FINANCE: { ...SHORTCUTS.GLOBAL, ...SHORTCUTS.FINANCE },
    TRANSPORT: { ...SHORTCUTS.GLOBAL, ...SHORTCUTS.TRANSPORT },
    CUSTOMER_SERVICE_MANAGER: { ...SHORTCUTS.GLOBAL, ...SHORTCUTS.CS, ...SHORTCUTS.MANAGER },
    FINANCE_MANAGER: { ...SHORTCUTS.GLOBAL, ...SHORTCUTS.FINANCE, ...SHORTCUTS.MANAGER },
    TRANSPORT_MANAGER: { ...SHORTCUTS.GLOBAL, ...SHORTCUTS.TRANSPORT, ...SHORTCUTS.MANAGER },
    ANALYST: { ...SHORTCUTS.GLOBAL },
    ADMIN: { ...SHORTCUTS.GLOBAL, ...SHORTCUTS.ADMIN },
  };

  return roleShortcuts[role] || SHORTCUTS.GLOBAL;
};

// Format shortcut for display
export const formatShortcut = (shortcut) => {
  const parts = [];

  if (shortcut.ctrlKey) parts.push('Ctrl');
  if (shortcut.shiftKey) parts.push('Shift');
  if (shortcut.altKey) parts.push('Alt');
  parts.push(shortcut.key.toUpperCase());

  return parts.join(' + ');
};

// Keyboard shortcut help modal content
export const ShortcutHelpContent = ({ role }) => {
  const shortcuts = getShortcutsForRole(role);

  return (
    <div className="keyboard-shortcuts-help">
      <h4>Keyboard Shortcuts</h4>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Action</th>
            <th>Shortcut</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(shortcuts).map(([key, shortcut]) => (
            <tr key={key}>
              <td>{shortcut.description}</td>
              <td>
                <kbd>{formatShortcut(shortcut)}</kbd>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Check if a key combination is pressed
export const isKeyCombo = (event, combo) => {
  const { key, ctrlKey = false, shiftKey = false, altKey = false } = combo;

  return (
    event.key.toLowerCase() === key.toLowerCase() &&
    event.ctrlKey === ctrlKey &&
    event.shiftKey === shiftKey &&
    event.altKey === altKey
  );
};
