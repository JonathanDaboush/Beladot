import React, { useState } from 'react';
import { Container, Row, Col, Nav, Alert, Card } from 'react-bootstrap';

/**
 * Manager Console (AWS Console style)
 * Department-specific employee management
 * ZERO cross-department access
 * Available to: FINANCE_MANAGER, TRANSPORT_MANAGER, CUSTOMER_SERVICE_MANAGER
 */
const ManagerConsole = () => {
  const [activeTab, setActiveTab] = useState('employees');

  return (
    <Container fluid className="vh-100">
      <Row className="h-100">
        {/* Sidebar */}
        <Col md={3} lg={2} className="bg-dark text-white p-0">
          <div className="p-3 border-bottom border-secondary">
            <h4>👔 Manager</h4>
          </div>
          <Nav className="flex-column">
            <Nav.Link
              className={`text-white ${activeTab === 'employees' ? 'bg-primary' : ''}`}
              onClick={() => setActiveTab('employees')}
            >
              👥 Employees
            </Nav.Link>
            <Nav.Link
              className={`text-white ${activeTab === 'leave' ? 'bg-primary' : ''}`}
              onClick={() => setActiveTab('leave')}
            >
              📅 Leave Requests
            </Nav.Link>
            <Nav.Link
              className={`text-white ${activeTab === 'schedules' ? 'bg-primary' : ''}`}
              onClick={() => setActiveTab('schedules')}
            >
              📆 Schedules
            </Nav.Link>
            <Nav.Link
              className={`text-white ${activeTab === 'performance' ? 'bg-primary' : ''}`}
              onClick={() => setActiveTab('performance')}
            >
              📈 Performance
            </Nav.Link>
          </Nav>
        </Col>

        {/* Main Content */}
        <Col md={9} lg={10} className="p-4">
          <h1 className="mb-4">{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</h1>

          <Alert variant="warning">
            <strong>⚠️ Department Manager:</strong> You can only manage
            employees in YOUR department. NO cross-department access.
          </Alert>

          <Card>
            <Card.Body>
              {activeTab === 'employees' && (
                <div>
                  <h3>Department Employees</h3>
                  <p>CRUD employee accounts within your department only</p>
                  <div className="text-center py-5">
                    <div style={{ fontSize: '4rem' }}>👥</div>
                    <p>Employee management interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'leave' && (
                <div>
                  <h3>Leave Requests</h3>
                  <p>Approve or deny sick days, PTO, and schedule changes</p>
                  <div className="text-center py-5">
                    <div style={{ fontSize: '4rem' }}>📅</div>
                    <p>Leave approval interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'schedules' && (
                <div>
                  <h3>Employee Schedules</h3>
                  <p>Manage schedules and approve shift swaps</p>
                  <div className="text-center py-5">
                    <div style={{ fontSize: '4rem' }}>📆</div>
                    <p>Schedule management interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'performance' && (
                <div>
                  <h3>Performance Logs</h3>
                  <p>Enter performance reviews and track employee progress</p>
                  <div className="text-center py-5">
                    <div style={{ fontSize: '4rem' }}>📈</div>
                    <p>Performance tracking interface coming soon</p>
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

export default ManagerConsole;
