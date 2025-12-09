import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * Home Page - Redirects to appropriate view based on user role
 */
const Home = () => {
  const { currentView, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading) {
      // Redirect based on current view
      const viewRoutes = {
        'customer': '/shop',
        'seller': '/seller',
        'cs-console': '/cs-console',
        'finance-console': '/finance',
        'transport-console': '/transport',
        'manager-console': '/manager',
        'analytics': '/analytics',
        'admin': '/admin',
      };

      const route = viewRoutes[currentView] || '/shop';
      navigate(route, { replace: true });
    }
  }, [currentView, loading, navigate]);

  if (loading) {
    return (
      <div className="loading-spinner">
        <div className="spinner"></div>
      </div>
    );
  }

  return null;
};

export default Home;
