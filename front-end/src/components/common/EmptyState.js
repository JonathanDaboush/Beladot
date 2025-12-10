import React from 'react';
import { Container, Button } from 'react-bootstrap';
import './EmptyState.css';

/**
 * Empty State Component
 * Displays friendly message when no data is available
 */
const EmptyState = ({
  icon = '📦',
  title = 'No items found',
  message = 'Try adjusting your filters or search terms.',
  actionLabel = null,
  onAction = null,
  style = {},
}) => {
  return (
    <Container
      className="empty-state"
      style={{
        textAlign: 'center',
        padding: '60px 20px',
        ...style,
      }}
    >
      <div className="empty-state-icon" style={{ fontSize: '64px', marginBottom: '16px' }}>
        {icon}
      </div>
      <h4 className="empty-state-title" style={{ marginBottom: '8px', color: '#333' }}>
        {title}
      </h4>
      <p className="empty-state-message" style={{ color: '#666', marginBottom: '24px' }}>
        {message}
      </p>
      {actionLabel && onAction && (
        <Button variant="primary" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </Container>
  );
};

// Specific empty state variants
export const EmptyCartState = ({ onContinueShopping }) => (
  <EmptyState
    icon="🛒"
    title="Your cart is empty"
    message="Add some products to get started!"
    actionLabel="Continue Shopping"
    onAction={onContinueShopping}
  />
);

export const EmptyProductsState = ({ onReset }) => (
  <EmptyState
    icon="🔍"
    title="No products found"
    message="Try adjusting your search or filters"
    actionLabel="Reset Filters"
    onAction={onReset}
  />
);

export const EmptyOrdersState = () => (
  <EmptyState
    icon="📦"
    title="No orders yet"
    message="Your order history will appear here once you make a purchase"
  />
);

export const EmptyTicketsState = () => (
  <EmptyState
    icon="✅"
    title="All caught up!"
    message="No pending support tickets"
  />
);

export const EmptyShipmentsState = () => (
  <EmptyState
    icon="🚚"
    title="No shipments"
    message="Shipments will appear here when orders are ready to ship"
  />
);

export const EmptyEmployeesState = ({ onAddEmployee }) => (
  <EmptyState
    icon="👥"
    title="No employees in this department"
    message="Add your first employee to get started"
    actionLabel="Add Employee"
    onAction={onAddEmployee}
  />
);

export default EmptyState;
