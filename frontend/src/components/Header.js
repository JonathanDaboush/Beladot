
import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import UserMenu from './UserMenu';
import NavBar from './NavBar';
import RoleIndicator from './RoleIndicator';
import RoleSwitcher from './RoleSwitcher';

import { ROLE_META } from './roles';

const Header = () => {
  const [categories, setCategories] = useState([]);
  const [search, setSearch] = useState('');
  const [dropdown, setDropdown] = useState(null);
  const { activeRole, availableRoles } = useAuth();
  const [switcherOpen, setSwitcherOpen] = useState(false);

  useEffect(() => {
    let mounted = true;
    const fetchCategories = async () => {
      try {
        const res = await fetch('/api/categories');
        const data = await res.json();
        if (mounted) {
          setCategories(Array.isArray(data.categories) ? data.categories : []);
        }
      } catch {
        if (mounted) setCategories([]);
      }
    };
    fetchCategories();
    return () => { mounted = false; };
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    window.location.href = `/search?query=${encodeURIComponent(search)}`;
  };

  const handleLogout = () => {
    // TODO: Implement logout logic (clear session, redirect, etc.)
    window.location.href = '/logout';
  };

  const accent = ROLE_META[activeRole]?.pillColor;
  return (
    <>
      <header className="header" role="banner" style={{ '--role-accent': accent }}>
        <div className="header-left">
          <span className="logo">Bela</span>
          <span className="app-name">Commerce</span>
        </div>
        <div className="header-center">
          {/* Unified nav; items scoped by activeRole */}
          <NavBar />
        </div>
        <div className="header-right">
          {/* Cart icon shown only in Customer (user) portal */}
          {activeRole === 'user' && (
            <a href="/cart" className="cart-icon" aria-label="Cart" title="Cart" style={{ textDecoration: 'none', fontSize: '1.25rem' }}>🛒</a>
          )}
          {/* Portal switcher visible only when more than one portal is available */}
          {availableRoles && availableRoles.length > 1 && (
            <>
              <RoleIndicator onClick={() => setSwitcherOpen(true)} />
              <RoleSwitcher open={switcherOpen} onClose={() => setSwitcherOpen(false)} />
            </>
          )}
          <UserMenu onLogout={handleLogout} />
        </div>
      </header>
    </>
  );
};

export default Header;
