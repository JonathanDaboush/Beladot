/**
 * Cart API
 *
 * Provides functions for interacting with cart endpoints.
 * All functions throw errors if requests fail.
 */

/**
 * Fetches all cart items for the current user.
 * @returns {Promise<Array>} List of cart items
 */
export async function fetchCartItems() {
  const res = await fetch('/api/cart');
  if (!res.ok) throw new Error('Failed to fetch cart items');
  return res.json();
}

/**
 * Edits the quantity of a specific cart item.
 * @param {string|number} itemId
 * @param {number} newQty
 * @returns {Promise<object>} Updated cart item
 */
export async function editCartItemQuantity(itemId, newQty) {
  const res = await fetch(`/api/cart/item/${itemId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ quantity: newQty })
  });
  if (!res.ok) throw new Error('Failed to update cart item');
  return res.json();
}

/**
 * Removes a cart item by ID.
 * @param {string|number} itemId
 * @returns {Promise<object>} Result of removal
 */
export async function removeCartItem(itemId) {
  const res = await fetch(`/api/cart/item/${itemId}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to remove cart item');
  return res.json();
}

/**
 * Adds an item to the authenticated user's cart.
 * Falls back silently if endpoint not available.
 * @param {{product_id:number, quantity:number, variant_id?:number}} payload
 * @returns {Promise<object>} Added cart item
 */
export async function addToCart(payload) {
  const res = await fetch('/api/v1/customer/cart/items', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: payload.product_id, quantity: payload.quantity, variant_id: payload.variant_id })
  });
  if (!res.ok) throw new Error('Failed to add to cart');
  return res.json();
}
