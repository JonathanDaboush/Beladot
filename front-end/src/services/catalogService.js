import api from './api';

/**
 * Catalog Service
 * Handles categories and catalog management (Admin operations)
 */
const catalogService = {
  // Get all categories (Public)
  getCategories: async (includeInactive = false) => {
    const response = await api.get(`/catalog/categories?include_inactive=${includeInactive}`);
    return response.data;
  },

  // Get category by ID
  getCategory: async (categoryId) => {
    const response = await api.get(`/catalog/categories/${categoryId}`);
    return response.data;
  },

  // Create category (Admin only)
  createCategory: async (categoryData) => {
    const response = await api.post('/catalog/categories', categoryData);
    return response.data;
  },

  // Update category (Admin only)
  updateCategory: async (categoryId, categoryData) => {
    const response = await api.put(`/catalog/categories/${categoryId}`, categoryData);
    return response.data;
  },

  // Delete category (Admin only)
  deleteCategory: async (categoryId) => {
    const response = await api.delete(`/catalog/categories/${categoryId}`);
    return response.data;
  },

  // Create subcategory (Admin only)
  createSubcategory: async (categoryId, subcategoryData) => {
    const response = await api.post(`/catalog/categories/${categoryId}/subcategories`, subcategoryData);
    return response.data;
  },

  // Update subcategory (Admin only)
  updateSubcategory: async (subcategoryId, subcategoryData) => {
    const response = await api.put(`/catalog/subcategories/${subcategoryId}`, subcategoryData);
    return response.data;
  },

  // Delete subcategory (Admin only)
  deleteSubcategory: async (subcategoryId) => {
    const response = await api.delete(`/catalog/subcategories/${subcategoryId}`);
    return response.data;
  },
};

export default catalogService;
