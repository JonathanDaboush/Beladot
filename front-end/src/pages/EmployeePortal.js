import React from 'react';
import { Container, Card, Alert } from 'react-bootstrap';

/**
 * Employee Base Portal
 * Clock in/out, schedule, leave requests
 * Available to: ALL employee types (CS, Finance, Transport, Managers)
 */
const EmployeePortal = () => {
  return (
    <Container className="py-5">
      <h1 className="mb-4">Employee Portal</h1>
      <Alert variant="info">
        <strong>ℹ️ Employee Portal:</strong> Clock in/out, view schedules, submit leave requests
      </Alert>
      <Card className="text-center p-5">
        <Card.Body>
          <div style={{ fontSize: '4rem' }}>👷</div>
          <h3 className="mt-3">Employee Features Coming Soon</h3>
          <p className="text-muted">Clock in/out, schedules, leave requests, and more</p>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default EmployeePortal;
