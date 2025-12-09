import React, { useState } from 'react';
import './AnalystDashboard.css';

/**
 * Analyst Dashboard (AWS Console style)
 * Read-only analytics and reports
 * ZERO write access, only aggregate data
 * Available to: ANALYST role only
 */
const AnalystDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="analyst-dashboard">
      <div className="console-container">
        {/* Sidebar */}
        <aside className="console-sidebar">
          <div className="sidebar-header">
            <h2>📊 Analytics</h2>
          </div>
          <nav className="sidebar-nav">
            <button
              className={`nav-item ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              📈 Overview
            </button>
            <button
              className={`nav-item ${activeTab === 'sales' ? 'active' : ''}`}
              onClick={() => setActiveTab('sales')}
            >
              💰 Sales Analytics
            </button>
            <button
              className={`nav-item ${activeTab === 'products' ? 'active' : ''}`}
              onClick={() => setActiveTab('products')}
            >
              📦 Product Analytics
            </button>
            <button
              className={`nav-item ${activeTab === 'customers' ? 'active' : ''}`}
              onClick={() => setActiveTab('customers')}
            >
              👥 Customer Analytics
            </button>
            <button
              className={`nav-item ${activeTab === 'reports' ? 'active' : ''}`}
              onClick={() => setActiveTab('reports')}
            >
              📄 Custom Reports
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
              <div className="alert alert-info">
                <strong>ℹ️ Analyst Role:</strong> Read-only access to aggregate
                business data. NO PII or write operations.
              </div>

              {activeTab === 'overview' && (
                <div>
                  <h3>Business Overview</h3>
                  <p>Key performance indicators and metrics</p>
                  <div className="empty-state">
                    <div className="empty-state-icon">📈</div>
                    <p>Analytics dashboard coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'sales' && (
                <div>
                  <h3>Sales Analytics</h3>
                  <p>Revenue trends, sales by category, and growth metrics</p>
                  <div className="empty-state">
                    <div className="empty-state-icon">💰</div>
                    <p>Sales analytics interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'products' && (
                <div>
                  <h3>Product Analytics</h3>
                  <p>Top products, inventory turnover, and product performance</p>
                  <div className="empty-state">
                    <div className="empty-state-icon">📦</div>
                    <p>Product analytics interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'customers' && (
                <div>
                  <h3>Customer Analytics</h3>
                  <p>Aggregate customer behavior and demographics (NO PII)</p>
                  <div className="empty-state">
                    <div className="empty-state-icon">👥</div>
                    <p>Customer analytics interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'reports' && (
                <div>
                  <h3>Custom Reports</h3>
                  <p>Generate and export custom data reports</p>
                  <div className="empty-state">
                    <div className="empty-state-icon">📄</div>
                    <p>Report builder coming soon</p>
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

export default AnalystDashboard;
