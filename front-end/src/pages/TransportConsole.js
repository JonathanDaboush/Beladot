import React, { useState } from 'react';
import { Container, Row, Col, Nav, Alert, Card } from 'react-bootstrap';

/**
 * Transport Console (AWS Console style)
 * Delivery management, shipment tracking, return handling
 * NO payment operations
 * Available to: TRANSPORT role only
 */
const TransportConsole = () => {
  const [activeTab, setActiveTab] = useState('shipments');

  return (
    <Container fluid className="vh-100">
      <Row className="h-100">
        {/* Sidebar */}
        <Col md={3} lg={2} className="bg-dark text-white p-0">
          <div className="p-3 border-bottom border-secondary">
            <h4>🚚 Transport</h4>
          </div>
          <Nav className="flex-column">
            <Nav.Link
              className={`text-white ${activeTab === 'shipments' ? 'bg-primary' : ''}`}
              onClick={() => setActiveTab('shipments')}
            >
              📦 Shipments
            </Nav.Link>
            <Nav.Link
              className={`text-white ${activeTab === 'fulfillment' ? 'bg-primary' : ''}`}
              onClick={() => setActiveTab('fulfillment')}
            >
              🏭 Fulfillment
            </Nav.Link>
            <Nav.Link
              className={`text-white ${activeTab === 'returns' ? 'bg-primary' : ''}`}
              onClick={() => setActiveTab('returns')}
            >
              ↩️ Returns
            </Nav.Link>
            <Nav.Link
              className={`text-white ${activeTab === 'tracking' ? 'bg-primary' : ''}`}
              onClick={() => setActiveTab('tracking')}
            >
              🔍 Tracking
            </Nav.Link>
          </Nav>
        </Col>

        {/* Main Content */}
        <Col md={9} lg={10} className="p-4">
          <h1 className="mb-4">{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</h1>

          <Alert variant="info">
            <strong>ℹ️ Transport Role:</strong> You can manage deliveries and
            shipments. NO payment modifications allowed.
          </Alert>

          <Card>
            <Card.Body>
              {activeTab === 'shipments' && (
                <div>
                  <h3>Shipment Management</h3>
                  <p>Update delivery statuses and manage active shipments</p>
                  <div className="text-center py-5">
                    <div style={{ fontSize: '4rem' }}>📦</div>
                    <p>Shipment management interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'fulfillment' && (
                <div>
                  <h3>Order Fulfillment</h3>
                  <p>Create shipments for pending orders</p>
                  <div className="text-center py-5">
                    <div style={{ fontSize: '4rem' }}>🏭</div>
                    <p>Fulfillment interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'returns' && (
                <div>
                  <h3>Return Processing</h3>
                  <p>Handle return shipments and update inventory</p>
                  <div className="text-center py-5">
                    <div style={{ fontSize: '4rem' }}>↩️</div>
                    <p>Return processing interface coming soon</p>
                  </div>
                </div>
              )}

              {activeTab === 'tracking' && (
                <div>
                  <h3>Shipment Tracking</h3>
                  <p>Track packages and view delivery status</p>
                  <div className="text-center py-5">
                    <div style={{ fontSize: '4rem' }}>🔍</div>
                    <p>Tracking interface coming soon</p>
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

export default TransportConsole;
