import React from 'react';
import { Pagination as BSPagination } from 'react-bootstrap';

/**
 * Pagination Component
 * Displays page navigation controls using Bootstrap Pagination
 */
const Pagination = ({ currentPage, totalPages, onPageChange, loading = false }) => {
  const pages = [];
  const maxPagesToShow = 5;

  let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
  let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

  if (endPage - startPage < maxPagesToShow - 1) {
    startPage = Math.max(1, endPage - maxPagesToShow + 1);
  }

  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }

  if (totalPages <= 1) return null;

  return (
    <BSPagination className="justify-content-center mt-4">
      <BSPagination.Prev
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1 || loading}
      />

      {startPage > 1 && (
        <>
          <BSPagination.Item onClick={() => onPageChange(1)} disabled={loading}>
            1
          </BSPagination.Item>
          {startPage > 2 && <BSPagination.Ellipsis disabled />}
        </>
      )}

      {pages.map((page) => (
        <BSPagination.Item
          key={page}
          active={page === currentPage}
          onClick={() => onPageChange(page)}
          disabled={loading}
        >
          {page}
        </BSPagination.Item>
      ))}

      {endPage < totalPages && (
        <>
          {endPage < totalPages - 1 && <BSPagination.Ellipsis disabled />}
          <BSPagination.Item
            onClick={() => onPageChange(totalPages)}
            disabled={loading}
          >
            {totalPages}
          </BSPagination.Item>
        </>
      )}

      <BSPagination.Next
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages || loading}
      />
    </BSPagination>
  );
};

export default Pagination;
