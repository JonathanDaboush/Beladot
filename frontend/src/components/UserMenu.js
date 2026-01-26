/**
 * UserMenu Component
 *
 * Displays a user menu with profile, account, order history, employee/seller options, and logout.
 * Handles menu state and options based on authentication and user role.
 *
 * Props:
 *   - onLogout: Function to call when user logs out
 */
import React, { useState } from 'react';
import './UserMenu.css';

import { useAuth } from '../context/AuthContext';

/**
 * Main user menu component.
 */
const UserMenu = ({ onLogout }) => {
  const [open, setOpen] = useState(false);
  const { user, isEmployee, isManager, isSeller } = useAuth();

  /**
   * Returns menu options based on user authentication and role.
   */
  const portals = () => {
    if (!user) return [];
    const p = ['Customer'];
    if (isSeller) p.push('Seller');
    if (isEmployee) p.push('Employee');
    if (isManager) p.push('Manager');
    return p;
  };

  const portalList = portals();

  return (
    <div className="user-menu-wrapper">
      {/* User icon toggles menu open/close */}
      <div className="user-icon" onClick={() => setOpen(!open)}>
        <span role="img" aria-label="user">👤</span>
      </div>
      {open && (
        <div className="user-dropdown">
              {/* Auth actions: show only relevant options, no disabled items */}
              {!user && (
                <>
                  <div className="user-dropdown-item" onClick={() => window.location.href = '/login'}>Sign in</div>
                  <div className="user-dropdown-item" onClick={() => window.location.href = '/register'}>Create Account</div>
                  <div className="user-dropdown-item" onClick={() => window.location.href = '/forgot-password'}>Forgot Password</div>
                </>
              )}
              {user && (
                <div className="user-dropdown-item" onClick={() => { onLogout && onLogout(); }}>Sign out</div>
              )}

              {/* Orders visible for logged-in users */}
              {user && (
                <div className="user-dropdown-item" onClick={() => window.location.href = '/orders'}>Order History / Purchases</div>
              )}
          {/* Portal switcher: only when more than one portal is available */}
          {user && portalList.length > 1 && (
            <>
              <div className="dropdown-section-label">Switch Portal</div>
              {portalList.includes('Customer') && (
                <div className="user-dropdown-item" onClick={() => window.location.href = '/'}>Customer</div>
              )}
              {portalList.includes('Seller') && (
                <div className="user-dropdown-item" onClick={() => window.location.href = '/seller'}>Seller</div>
              )}
              {portalList.includes('Employee') && (
                <div className="user-dropdown-item" onClick={() => window.location.href = '/employee'}>Employee</div>
              )}
              {portalList.includes('Manager') && (
                <div className="user-dropdown-item" onClick={() => window.location.href = '/manager'}>Manager</div>
              )}
            </>
          )}
          {/* Profile entry */}
          {user && (
            <div className="user-dropdown-item" onClick={() => { window.location.href = '/profile'; }}>Profile / Account</div>
          )}
          {/* Become a Seller: always last option */}
          {/* Not signed in: send to login with next to seller upgrade */}
          {!user && (
            <div className="user-dropdown-item" onClick={() => { window.location.href = '/login?next=/seller/upgrade'; }}>Become a Seller</div>
          )}
          {/* Signed in but not a seller: go to seller upgrade */}
          {user && !isSeller && (
            <div className="user-dropdown-item" onClick={() => { window.location.href = '/seller/upgrade'; }}>Become a Seller</div>
          )}
        </div>
      )}
    </div>
  );
};

export default UserMenu;
