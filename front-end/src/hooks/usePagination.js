import { useState, useCallback } from 'react';

/**
 * Pagination Hook
 * Manages pagination state and URL sync
 */
const usePagination = (initialPage = 1, initialLimit = 20) => {
  const [page, setPage] = useState(initialPage);
  const [limit, setLimit] = useState(initialLimit);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  // Go to specific page
  const goToPage = useCallback((pageNum) => {
    setPage(Math.max(1, Math.min(pageNum, totalPages)));
  }, [totalPages]);

  // Next page
  const nextPage = useCallback(() => {
    if (page < totalPages) {
      setPage((prev) => prev + 1);
    }
  }, [page, totalPages]);

  // Previous page
  const prevPage = useCallback(() => {
    if (page > 1) {
      setPage((prev) => prev - 1);
    }
  }, [page]);

  // Update pagination info from API response
  const updatePagination = useCallback((response) => {
    if (response.total_pages) setTotalPages(response.total_pages);
    if (response.total_items) setTotalItems(response.total_items);
    if (response.current_page) setPage(response.current_page);
  }, []);

  // Reset to first page
  const reset = useCallback(() => {
    setPage(1);
  }, []);

  return {
    page,
    limit,
    totalPages,
    totalItems,
    goToPage,
    nextPage,
    prevPage,
    setLimit,
    updatePagination,
    reset,
    hasNextPage: page < totalPages,
    hasPrevPage: page > 1,
  };
};

export default usePagination;
