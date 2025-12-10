import React, { useState } from 'react';
import { Container, Row, Col, Nav, Alert, Card } from 'react-bootstrap';

/**
 * Finance Console (AWS Console style)
 * Payroll, employee payments, financial reports
 * NO product or transport operations
 * Available to: FINANCE role only
 */
const FinanceConsole = () => {
  const [activeTab, setActiveTab] = useState('payroll');

  return (
    <Container fluid className="vh-100">
      <Row className="h-100">
        {/* Sidebar */}
        <Col md={3} lg={2} className="bg-dark text-white p-0">
          <div className="p-3 border-bottom border-secondary">
            <h4>💰 Finance</h4>
          </div>
          <Nav className="flex-column">
            <Nav.Link
              className={`text-white ${activeTab === 'payroll' ? 'bg-primary' : ''}`}
              onClick={() => setActiveTab('payroll')}
            >
              💵 Payroll
            </Nav.Link>
            <Nav.Link
              className={`text-white ${activeTab === 'employees' ? 'bg-primary' : ''}`}
              onClick={() => setActiveTab('employees')}
            >
              👥 Employee Payments
            </Nav.Link>
            <Nav.Link
              className={`text-white ${activeTab === 'payouts' ? 'bg-primary' : ''}`}
              onClick={() => setActiveTab('payouts')}
            >
              💳 Seller Payouts
            </Nav.Link>
            <Nav.Link
              className={`text-white ${activeTab === 'reports' ? 'bg-primary' : ''}`}
              onClick={() => setActiveTab('reports')}
            >
              📊 Financial Reports
            </Nav.Link>
          </Nav>
        </Col>

        {/* Main Content */}
        <Col md={9} lg={10} className="p-4">
          <h1 className="mb-4">{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</h1>

          <Alert variant="info">
            <strong>ℹ️ Finance Role:</strong> You can manage payroll and
            employee payments. NO product or transport operations allowed.
          </Alert>

          <Card>
            <Card.Body>
              {activeTab === 'payroll' && (
                <div>
                  <h3>Payroll Management</h3>
                  <p>Create and process employee payroll</p>
                  <div className="text-center py-5">
                    <div style={{ fontSize: '4rem' }}>💵</div>
                    <p>Payroll management interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'employees' && (
                <div>
                  <h3>Employee Payment Information</h3>
                  <p>Edit employee payment details and view payment history</p>
                  <div className="text-center py-5">
                    <div style={{ fontSize: '4rem' }}>👥</div>
                    <p>Employee payment interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'payouts' && (
                <div>
                  <h3>Seller Payouts</h3>
                  <p>Process payments to sellers for completed orders</p>
                  <div className="text-center py-5">
                    <div style={{ fontSize: '4rem' }}>💳</div>
                    <p>Seller payout interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'reports' && (
                <div>
                  <h3>Financial Reports</h3>
                  <p>View revenue, expenses, and financial summaries</p>
                  <div className="text-center py-5">
                    <div style={{ fontSize: '4rem' }}>📊</div>
                    <p>Financial reports interface coming soon</p>
                  </div>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default FinanceConsole;
