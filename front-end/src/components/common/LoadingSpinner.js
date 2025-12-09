import React from 'react';
import { Spinner } from 'react-bootstrap';

/**
 * Loading Spinner Component
 * Reusable loading indicator using Bootstrap Spinner
 */
const LoadingSpinner = ({ size = 'medium', fullScreen = false }) => {
  const sizeMap = {
    small: 'sm',
    medium: undefined,
    large: undefined
  };

  const spinnerSize = sizeMap[size];
  const animation = size === 'large' ? 'grow' : 'border';

  if (fullScreen) {
    return (
      <div 
        className="d-flex align-items-center justify-content-center" 
        style={{ minHeight: '100vh' }}
      >
        <Spinner animation={animation} role="status" size={spinnerSize} variant="primary">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
  }

  return (
    <div className="d-flex justify-content-center p-3">
      <Spinner animation={animation} role="status" size={spinnerSize} variant="primary">
        <span className="visually-hidden">Loading...</span>
      </Spinner>
    </div>
  );
};

export default LoadingSpinner;
