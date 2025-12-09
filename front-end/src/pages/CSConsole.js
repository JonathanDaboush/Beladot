import React, { useState } from 'react';
import { Container, Row, Col, Nav, Alert, Card } from 'react-bootstrap';

/**
 * Customer Service Console (AWS Console style)
 * Ticket management, refund/return approvals with MANDATORY LOGGING
 * Available to: CUSTOMER_SERVICE role only
 */
const CSConsole = () => {
  const [activeTab, setActiveTab] = useState('tickets');
  const [loading, setLoading] = useState(false);
  const [actionReason, setActionReason] = useState('');

  const handleActionWithLogging = async (action, reason) => {
    if (!reason.trim()) {
      alert('Action reason is required for audit logging');
      return;
    }

    try {
      setLoading(true);
      await action(reason);
      alert('Action completed and logged');
      setActionReason('');
    } catch (err) {
      alert('Action failed: ' + (err.response?.data?.detail || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container fluid className="vh-100">
      <Row className="h-100">
        {/* Sidebar */}
        <Col md={3} lg={2} className="bg-dark text-white p-0">
          <div className="p-3 border-bottom border-secondary">
            <h4>🎧 Customer Service</h4>
          </div>
          <Nav className="flex-column">
            <Nav.Link
              className={`text-white ${activeTab === 'tickets' ? 'bg-primary' : ''}`}
              onClick={() => setActiveTab('tickets')}
            >
              🎫 Tickets
            </Nav.Link>
            <Nav.Link
              className={`text-white ${activeTab === 'refunds' ? 'bg-primary' : ''}`}
              onClick={() => setActiveTab('refunds')}
            >
              💰 Refunds
            </Nav.Link>
            <Nav.Link
              className={`text-white ${activeTab === 'returns' ? 'bg-primary' : ''}`}
              onClick={() => setActiveTab('returns')}
            >
              📦 Returns
            </Nav.Link>
            <Nav.Link
              className={`text-white ${activeTab === 'audit' ? 'bg-primary' : ''}`}
              onClick={() => setActiveTab('audit')}
            >
              📋 Audit Logs
            </Nav.Link>
          </Nav>
        </Col>

        {/* Main Content */}
        <Col md={9} lg={10} className="p-4">
          <h1 className="mb-4">{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</h1>

          <Alert variant="warning">
            <strong>⚠️ Mandatory Logging:</strong> All customer service actions
            require a reason and are automatically logged for audit purposes.
          </Alert>

          <Card>
            <Card.Body>
              {activeTab === 'tickets' && (
                <div>
                  <h3>Support Tickets</h3>
                  <p>View and manage customer support tickets</p>
                  <div className="text-center py-5">
                    <div style={{ fontSize: '4rem' }}>🎫</div>
                    <p>Ticket management interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'refunds' && (
                <div>
                  <h3>Refund Requests</h3>
                  <p>Approve or deny refund requests based on business rules</p>
                  <div className="text-center py-5">
                    <div style={{ fontSize: '4rem' }}>💰</div>
                    <p>Refund management interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'returns' && (
                <div>
                  <h3>Return Requests</h3>
                  <p>Process product return requests</p>
                  <div className="text-center py-5">
                    <div style={{ fontSize: '4rem' }}>📦</div>
                    <p>Return management interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'audit' && (
                <div>
                  <h3>Audit Logs</h3>
                  <p>View all customer service actions and impersonations</p>
                  <div className="text-center py-5">
                    <div style={{ fontSize: '4rem' }}>📋</div>
                    <p>Audit log viewer coming soon</p>
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

export default CSConsole;
