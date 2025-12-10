import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { CartProvider } from './contexts/CartContext';
import { FeatureFlagProvider } from './contexts/FeatureFlagContext';
import { ToastProvider } from './contexts/ToastContext';
import ErrorBoundary from './components/common/ErrorBoundary';
import ProtectedRoute from './components/common/ProtectedRoute';
import Header from './components/common/Header';
import Login from './pages/Login';
import Register from './pages/Register';
import Home from './pages/Home';
import CustomerView from './pages/CustomerView';
import SellerPortal from './pages/SellerPortal';
import EmployeePortal from './pages/EmployeePortal';
import CSConsole from './pages/CSConsole';
import FinanceConsole from './pages/FinanceConsole';
import TransportConsole from './pages/TransportConsole';
import ManagerConsole from './pages/ManagerConsole';
import AnalystDashboard from './pages/AnalystDashboard';
import AdminConsole from './pages/AdminConsole';
import Unauthorized from './pages/Unauthorized';
import useKeyboardShortcuts from './hooks/useKeyboardShortcuts';
import './App.css';

// Wrapper component for keyboard shortcuts
const AppContent = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  useKeyboardShortcuts(navigate, user);

  return (
    <div className="App">
      <Header />
      <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/unauthorized" element={<Unauthorized />} />

            {/* Protected Routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Home />
                </ProtectedRoute>
              }
            />

            {/* Customer Shopping View */}
            <Route
              path="/shop"
              element={
                <ProtectedRoute>
                  <CustomerView />
                </ProtectedRoute>
              }
            />

            {/* Seller Portal */}
            <Route
              path="/seller"
              element={
                <ProtectedRoute requiredView="seller">
                  <SellerPortal />
                </ProtectedRoute>
              }
            />

            {/* Employee Portal */}
            <Route
              path="/employee"
              element={
                <ProtectedRoute>
                  <EmployeePortal />
                </ProtectedRoute>
              }
            />

            {/* Customer Service Console */}
            <Route
              path="/cs-console"
              element={
                <ProtectedRoute requiredView="cs-console">
                  <CSConsole />
                </ProtectedRoute>
              }
            />

            {/* Finance Console */}
            <Route
              path="/finance"
              element={
                <ProtectedRoute requiredView="finance-console">
                  <FinanceConsole />
                </ProtectedRoute>
              }
            />

            {/* Transport Console */}
            <Route
              path="/transport"
              element={
                <ProtectedRoute requiredView="transport-console">
                  <TransportConsole />
                </ProtectedRoute>
              }
            />

            {/* Manager Console */}
            <Route
              path="/manager"
              element={
                <ProtectedRoute requiredView="manager-console">
                  <ManagerConsole />
                </ProtectedRoute>
              }
            />

            {/* Analyst Dashboard */}
            <Route
              path="/analytics"
              element={
                <ProtectedRoute requiredView="analytics">
                  <AnalystDashboard />
                </ProtectedRoute>
              }
            />

            {/* Admin Console */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute requiredView="admin">
                  <AdminConsole />
                </ProtectedRoute>
              }
            />

            {/* Catch all */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      );
    };

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <ToastProvider>
          <AuthProvider>
            <CartProvider>
              <FeatureFlagProvider>
                <AppContent />
              </FeatureFlagProvider>
            </CartProvider>
          </AuthProvider>
        </ToastProvider>
      </Router>
    </ErrorBoundary>
  );
}

export default App;