import api from './api';

/**
 * Search Service
 * Handles product search with filters
 */
const searchService = {
  // Search products by keyword
  searchProducts: async (query, filters = {}) => {
    const params = {
      query,
      ...filters,
    };
    const response = await api.get('/search/products', { params });
    return response.data;
  },

  // Advanced product filtering
  filterProducts: async (filters) => {
    const response = await api.post('/search/products/filter', filters);
    return response.data;
  },

  // Get search suggestions/autocomplete
  getSearchSuggestions: async (query) => {
    const response = await api.get(`/search/suggestions?query=${query}`);
    return response.data;
  },
};

export default searchService;
