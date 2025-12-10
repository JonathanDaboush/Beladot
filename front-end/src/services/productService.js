import api from './api';

/**
 * Product Service
 * Handles product browsing, search, categories
 */
const productService = {
  // Get all products with pagination and filters
  getProducts: async (params = {}) => {
    const {
      page = 1,
      pageSize = 20,
      currency = 'USD',
      mainCategoryId = null,
      mainSubcategoryId = null,
    } = params;
    
    const queryParams = new URLSearchParams({
      page,
      page_size: pageSize,
      currency,
    });
    
    if (mainCategoryId) queryParams.append('main_category_id', mainCategoryId);
    if (mainSubcategoryId) queryParams.append('main_subcategory_id', mainSubcategoryId);
    
    const response = await api.get(`/products?${queryParams}`);
    return response.data;
  },

  // Get single product with currency support
  getProduct: async (productId, currency = 'USD') => {
    const response = await api.get(`/products/${productId}?currency=${currency}`);
    return response.data;
  },

  // Search products
  searchProducts: async (query, filters = {}) => {
    const response = await api.post('/search', { query, ...filters });
    return response.data;
  },

  // Get categories
  getCategories: async () => {
    const response = await api.get('/catalog/categories');
    return response.data;
  },

  // Get product reviews
  getProductReviews: async (productId, page = 1) => {
    const response = await api.get(`/products/${productId}/reviews?page=${page}`);
    return response.data;
  },

  // Add product review (authenticated)
  addReview: async (productId, reviewData) => {
    const response = await api.post(`/products/${productId}/reviews`, reviewData);
    return response.data;
  },

  // === SELLER ENDPOINTS ===
  
  // Create product (Seller only)
  createProduct: async (productData) => {
    const response = await api.post('/catalog/products', productData);
    return response.data;
  },

  // Update product (Seller only)
  updateProduct: async (productId, productData) => {
    const response = await api.put(`/catalog/products/${productId}`, productData);
    return response.data;
  },

  // Delete product (Seller only)
  deleteProduct: async (productId) => {
    const response = await api.delete(`/catalog/products/${productId}`);
    return response.data;
  },

  // Create product variant (Seller only)
  createVariant: async (productId, variantData) => {
    const response = await api.post(`/catalog/products/${productId}/variants`, variantData);
    return response.data;
  },

  // Update product variant (Seller only)
  updateVariant: async (variantId, variantData) => {
    const response = await api.put(`/catalog/variants/${variantId}`, variantData);
    return response.data;
  },

  // Upload product image (Seller only)
  uploadProductImage: async (productId, formData) => {
    const response = await api.post(`/catalog/products/${productId}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // Delete product image (Seller only)
  deleteProductImage: async (productId, imageId) => {
    const response = await api.delete(`/catalog/products/${productId}/images/${imageId}`);
    return response.data;
  },
};

export default productService;
