import React, { createContext, useContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import authService from '../services/authService';
import { TokenManager } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentView, setCurrentView] = useState('customer');

  // Initialize auth state on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const token = TokenManager.getAccessToken();
      const savedUser = localStorage.getItem('user');
      const savedView = localStorage.getItem('currentView');

      if (token && !TokenManager.isTokenExpired(token)) {
        try {
          // Restore user from localStorage or fetch from API
          if (savedUser) {
            const parsedUser = JSON.parse(savedUser);
            setUser(parsedUser);
            setCurrentView(savedView || getDefaultView(parsedUser.role));
          } else {
            const userData = await authService.getCurrentUser();
            setUser(userData);
            localStorage.setItem('user', JSON.stringify(userData));
            setCurrentView(savedView || getDefaultView(userData.role));
          }
        } catch (error) {
          console.error('Failed to initialize auth:', error);
          TokenManager.clearTokens();
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  // Get default view based on role
  const getDefaultView = (role) => {
    const roleViewMap = {
      'customer': 'customer',
      'seller': 'customer', // Sellers default to shopping, can switch to seller portal
      'customer_service': 'cs-console',
      'finance': 'finance-console',
      'transport': 'transport-console',
      'analyst': 'analytics',
      'admin': 'admin',
    };

    // Handle manager roles
    if (role?.includes('manager')) {
      return 'manager-console';
    }

    return roleViewMap[role] || 'customer';
  };

  // Get available views based on user roles
  const getAvailableViews = (userRole, userRoles = []) => {
    const views = [];

    // Admin can access everything
    if (userRole === 'admin') {
      return [
        { label: 'Admin Console', value: 'admin', icon: '⚙️' },
        { label: '--- Switch Role ---', value: 'divider', disabled: true },
        { label: 'View as Customer', value: 'customer', icon: '🛍️' },
        { label: 'View as Seller', value: 'seller', icon: '🏪' },
        { label: 'View as Customer Service', value: 'cs-console', icon: '🎧' },
        { label: 'View as Finance', value: 'finance-console', icon: '💰' },
        { label: 'View as Transport', value: 'transport-console', icon: '🚚' },
        { label: 'View as Manager', value: 'manager-console', icon: '👔' },
        { label: 'View as Analyst', value: 'analytics', icon: '📊' },
      ];
    }

    // Base views
    if (userRole === 'customer' || userRoles.includes('customer')) {
      views.push({ label: 'Shop', value: 'customer', icon: '🛍️' });
    }

    if (userRole === 'seller' || userRoles.includes('seller')) {
      views.push({ label: 'Seller Portal', value: 'seller', icon: '🏪' });
    }

    // Employee divisions
    if (userRole === 'customer_service') {
      views.push({ label: 'Customer Service', value: 'cs-console', icon: '🎧' });
    }

    if (userRole === 'finance') {
      views.push({ label: 'Finance', value: 'finance-console', icon: '💰' });
    }

    if (userRole === 'transport') {
      views.push({ label: 'Transport', value: 'transport-console', icon: '🚚' });
    }

    // Manager
    if (userRole?.includes('manager')) {
      views.push({ label: 'Manager', value: 'manager-console', icon: '👔' });
    }

    // Analyst
    if (userRole === 'analyst') {
      views.push({ label: 'Analytics', value: 'analytics', icon: '📊' });
    }

    return views;
  };

  // Login
  const login = async (email, password) => {
    const data = await authService.login(email, password);
    TokenManager.setTokens(data.access_token, data.refresh_token);
    
    const userData = await authService.getCurrentUser();
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
    
    const defaultView = getDefaultView(userData.role);
    setCurrentView(defaultView);
    localStorage.setItem('currentView', defaultView);
    
    return userData;
  };

  // Register
  const register = async (userData) => {
    const data = await authService.register(userData);
    TokenManager.setTokens(data.access_token, data.refresh_token);
    
    const user = await authService.getCurrentUser();
    setUser(user);
    localStorage.setItem('user', JSON.stringify(user));
    
    const defaultView = getDefaultView(user.role);
    setCurrentView(defaultView);
    localStorage.setItem('currentView', defaultView);
    
    return user;
  };

  // Logout
  const logout = async () => {
    await authService.logout();
    setUser(null);
    setCurrentView('customer');
  };

  // Switch view
  const switchView = (view) => {
    setCurrentView(view);
    localStorage.setItem('currentView', view);
    
    // For admin, track impersonation
    if (user?.role === 'admin' && view !== 'admin') {
      localStorage.setItem('adminImpersonating', view);
    } else {
      localStorage.removeItem('adminImpersonating');
    }
  };

  // Check if user has permission for a view
  const hasViewAccess = (view) => {
    if (!user) return false;
    if (user.role === 'admin') return true;

    const viewRoleMap = {
      'customer': ['customer', 'seller', 'customer_service'],
      'seller': ['seller'],
      'cs-console': ['customer_service'],
      'finance-console': ['finance'],
      'transport-console': ['transport'],
      'manager-console': ['manager', 'finance_manager', 'transport_manager', 'customer_service_manager'],
      'analytics': ['analyst'],
      'admin': ['admin'],
    };

    const allowedRoles = viewRoleMap[view] || [];
    return allowedRoles.some(role => user.role.includes(role));
  };

  const value = {
    user,
    loading,
    currentView,
    login,
    register,
    logout,
    switchView,
    getAvailableViews,
    hasViewAccess,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
