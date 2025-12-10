import React from 'react';
import { Container, Spinner } from 'react-bootstrap';
import './LoadingSkeleton.css';

/**
 * Loading Skeleton Component
 * Provides placeholder UI while data is loading
 */

// Generic skeleton loader
export const SkeletonBox = ({ width = '100%', height = '20px', style = {} }) => (
  <div
    className="skeleton-box"
    style={{
      width,
      height,
      backgroundColor: '#e0e0e0',
      borderRadius: '4px',
      animation: 'skeleton-pulse 1.5s ease-in-out infinite',
      ...style,
    }}
  />
);

// Product card skeleton
export const ProductCardSkeleton = () => (
  <div className="product-card-skeleton" style={{ padding: '16px' }}>
    <SkeletonBox width="100%" height="200px" style={{ marginBottom: '12px' }} />
    <SkeletonBox width="80%" height="20px" style={{ marginBottom: '8px' }} />
    <SkeletonBox width="60%" height="16px" style={{ marginBottom: '8px' }} />
    <SkeletonBox width="40%" height="24px" style={{ marginBottom: '12px' }} />
    <SkeletonBox width="100%" height="40px" />
  </div>
);

// Table row skeleton
export const TableRowSkeleton = ({ columns = 4 }) => (
  <tr>
    {[...Array(columns)].map((_, index) => (
      <td key={index}>
        <SkeletonBox height="16px" />
      </td>
    ))}
  </tr>
);

// Table skeleton (for dense employee views)
export const TableSkeleton = ({ rows = 5, columns = 4 }) => (
  <table className="table">
    <thead>
      <tr>
        {[...Array(columns)].map((_, index) => (
          <th key={index}>
            <SkeletonBox height="20px" />
          </th>
        ))}
      </tr>
    </thead>
    <tbody>
      {[...Array(rows)].map((_, rowIndex) => (
        <TableRowSkeleton key={rowIndex} columns={columns} />
      ))}
    </tbody>
  </table>
);

// Full screen loading spinner
export const FullScreenLoader = ({ message = 'Loading...' }) => (
  <Container
    fluid
    className="d-flex flex-column justify-content-center align-items-center"
    style={{ minHeight: '100vh' }}
  >
    <Spinner animation="border" role="status" variant="primary" style={{ width: '3rem', height: '3rem' }}>
      <span className="visually-hidden">Loading...</span>
    </Spinner>
    <p className="mt-3 text-muted">{message}</p>
  </Container>
);

// List skeleton
export const ListSkeleton = ({ items = 5 }) => (
  <div>
    {[...Array(items)].map((_, index) => (
      <div key={index} style={{ marginBottom: '12px', padding: '12px', border: '1px solid #e0e0e0', borderRadius: '4px' }}>
        <SkeletonBox width="70%" height="18px" style={{ marginBottom: '8px' }} />
        <SkeletonBox width="50%" height="14px" />
      </div>
    ))}
  </div>
);

export default {
  SkeletonBox,
  ProductCardSkeleton,
  TableRowSkeleton,
  TableSkeleton,
  FullScreenLoader,
  ListSkeleton,
};
