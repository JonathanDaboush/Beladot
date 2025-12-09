import React from 'react';
import { Container, Alert, Button } from 'react-bootstrap';

/**
 * Error Boundary Component
 * Catches React errors and displays fallback UI using Bootstrap
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Container className="d-flex align-items-center justify-content-center min-vh-100">
          <Alert variant="danger" className="text-center p-5" style={{ maxWidth: '600px' }}>
            <Alert.Heading>
              <span style={{ fontSize: '3rem' }}>⚠️</span>
              <h2 className="mt-3">Something went wrong</h2>
            </Alert.Heading>
            <p className="mb-4">
              {this.state.error?.message || 'An unexpected error occurred'}
            </p>
            <Button
              variant="primary"
              onClick={() => window.location.reload()}
            >
              Reload Page
            </Button>
          </Alert>
        </Container>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
