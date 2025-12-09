import React, { useState } from 'react';
import './AdminConsole.css';

/**
 * Admin Console (AWS Console style)
 * Full system access - user management, system config, ALL operations
 * Available to: ADMIN role only
 */
const AdminConsole = () => {
  const [activeTab, setActiveTab] = useState('users');

  return (
    <div className="admin-console">
      <div className="console-container">
        {/* Sidebar */}
        <aside className="console-sidebar">
          <div className="sidebar-header">
            <h2>⚙️ Admin</h2>
          </div>
          <nav className="sidebar-nav">
            <button
              className={`nav-item ${activeTab === 'users' ? 'active' : ''}`}
              onClick={() => setActiveTab('users')}
            >
              👥 Users
            </button>
            <button
              className={`nav-item ${activeTab === 'products' ? 'active' : ''}`}
              onClick={() => setActiveTab('products')}
            >
              📦 Products
            </button>
            <button
              className={`nav-item ${activeTab === 'orders' ? 'active' : ''}`}
              onClick={() => setActiveTab('orders')}
            >
              🛒 Orders
            </button>
            <button
              className={`nav-item ${activeTab === 'config' ? 'active' : ''}`}
              onClick={() => setActiveTab('config')}
            >
              ⚙️ Configuration
            </button>
            <button
              className={`nav-item ${activeTab === 'features' ? 'active' : ''}`}
              onClick={() => setActiveTab('features')}
            >
              🎛️ Feature Flags
            </button>
            <button
              className={`nav-item ${activeTab === 'audit' ? 'active' : ''}`}
              onClick={() => setActiveTab('audit')}
            >
              📋 Audit Logs
            </button>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="console-main">
          <div className="console-header">
            <h1>{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</h1>
          </div>

          <div className="console-content">
            <div className="card">
              <div className="alert alert-danger">
                <strong>⚠️ Admin Access:</strong> You have full system access.
                All actions are logged. Critical operations require confirmation.
              </div>

              {activeTab === 'users' && (
                <div>
                  <h3>User Management</h3>
                  <p>
                    Create, edit, deactivate users. Reset passwords. Assign roles.
                  </p>
                  <div className="empty-state">
                    <div className="empty-state-icon">👥</div>
                    <p>User management interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'products' && (
                <div>
                  <h3>Product Management (All Sellers)</h3>
                  <p>Modify ANY product from ANY seller</p>
                  <div className="empty-state">
                    <div className="empty-state-icon">📦</div>
                    <p>Product management interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'orders' && (
                <div>
                  <h3>Order Management (All Orders)</h3>
                  <p>View and modify ALL orders in the system</p>
                  <div className="empty-state">
                    <div className="empty-state-icon">🛒</div>
                    <p>Order management interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'config' && (
                <div>
                  <h3>System Configuration</h3>
                  <p>Tax rates, shipping rates, payment gateways, API keys</p>
                  <div className="empty-state">
                    <div className="empty-state-icon">⚙️</div>
                    <p>System configuration interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'features' && (
                <div>
                  <h3>Feature Flags</h3>
                  <p>Enable/disable features system-wide</p>
                  <div className="empty-state">
                    <div className="empty-state-icon">🎛️</div>
                    <p>Feature flag management coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'audit' && (
                <div>
                  <h3>Audit Logs (Full System)</h3>
                  <p>View ALL system activity and admin actions</p>
                  <div className="empty-state">
                    <div className="empty-state-icon">📋</div>
                    <p>Audit log viewer coming soon</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default AdminConsole;
