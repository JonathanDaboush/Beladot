import React from 'react';
import { Link } from 'react-router-dom';
import { Container, Alert, Button } from 'react-bootstrap';

const Unauthorized = () => {
  return (
    <Container className="d-flex align-items-center justify-content-center min-vh-100">
      <Alert variant="danger" className="text-center p-5" style={{ maxWidth: '600px' }}>
        <div style={{ fontSize: '5rem', fontWeight: 'bold', color: '#dc3545' }}>403</div>
        <Alert.Heading className="mt-3">Access Denied</Alert.Heading>
        <p className="mb-3">You don't have permission to access this page.</p>
        <p className="text-muted mb-4">
          If you believe this is an error, please contact your administrator.
        </p>
        <Button variant="primary" as={Link} to="/">
          Go to Home
        </Button>
      </Alert>
    </Container>
  );
};

export default Unauthorized;
