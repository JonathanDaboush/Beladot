import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { fetchCartItems, editCartItemQuantity, removeCartItem } from '../api/cart';
import { getGuestCart, updateGuestCartItem, removeGuestCartItem, mapGuestItemsForDisplay } from '../cart/guestCart';

const CartPage = () => {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const loadCart = async () => {
      setLoading(true);
      setError(null);
      try {
        if (!user) {
          const guestItems = getGuestCart();
          setCartItems(mapGuestItemsForDisplay(guestItems));
        } else {
          const data = await fetchCartItems();
          const items = (data.items || []).map((item) => ({
            id: item.variant_id || item.product_id,
            product: {
              name: item.product_name,
              image_url: item.product_image,
              category: item.category,
              subcategory: item.subcategory,
            },
            variant: item.variant_id ? {
              name: item.variant_name,
              image_url: item.variant_image,
            } : null,
            quantity: item.quantity,
            price: item.price,
            total: item.price * item.quantity,
          }));
          setCartItems(items);
        }
      } catch (e) {
        setError(e.message);
      }
      setLoading(false);
    };
    loadCart();
  }, [user]);

  const handleEditQuantity = async (itemId, newQty) => {
    try {
      if (!user) {
        const updated = updateGuestCartItem(itemId, newQty);
        setCartItems(mapGuestItemsForDisplay(updated));
      } else {
        await editCartItemQuantity(itemId, newQty);
        const data = await fetchCartItems();
        const items = (data.items || []).map((item) => ({
          id: item.variant_id || item.product_id,
          product: {
            name: item.product_name,
            image_url: item.product_image,
            category: item.category,
            subcategory: item.subcategory,
          },
          variant: item.variant_id ? {
            name: item.variant_name,
            image_url: item.variant_image,
          } : null,
          quantity: item.quantity,
          price: item.price,
          total: item.price * item.quantity,
        }));
        setCartItems(items);
      }
    } catch (e) {
      setError(e.message);
    }
  };

  const handleRemove = async (itemId) => {
    try {
      if (!user) {
        const updated = removeGuestCartItem(itemId);
        setCartItems(mapGuestItemsForDisplay(updated));
      } else {
        await removeCartItem(itemId);
        const data = await fetchCartItems();
        const items = (data.items || []).map((item) => ({
          id: item.variant_id || item.product_id,
          product: {
            name: item.product_name,
            image_url: item.product_image,
            category: item.category,
            subcategory: item.subcategory,
          },
          variant: item.variant_id ? {
            name: item.variant_name,
            image_url: item.variant_image,
          } : null,
          quantity: item.quantity,
          price: item.price,
          total: item.price * item.quantity,
        }));
        setCartItems(items);
      }
    } catch (e) {
      setError(e.message);
    }
  };

  const cartTotal = useMemo(() => cartItems.reduce((sum, item) => sum + item.total, 0), [cartItems]);

  return (
    <div className="container py-4">
      <h2 className="mb-4">Your Cart</h2>
      {loading ? (
        <div className="alert alert-info">Loading...</div>
      ) : error ? (
        <div className="alert alert-danger">{error}</div>
      ) : (
        <div className="row g-3">
          {cartItems.length === 0 ? (
            <div className="col-12">
              <div className="alert alert-secondary text-center">Your cart is empty.</div>
            </div>
          ) : (
            cartItems.map(item => (
              <div className="col-md-6 col-lg-4" key={item.id}>
                <div className="card h-100">
                  <div className="row g-0 align-items-center">
                    <div className="col-4">
                      <img
                        src={item.variant?.image_url || item.product.image_url}
                        alt={item.variant?.name || item.product.name}
                        className="img-fluid rounded-start"
                      />
                    </div>
                    <div className="col-8">
                      <div className="card-body">
                        <h5 className="card-title mb-1">{item.product.name}</h5>
                        <div className="text-muted small mb-1">
                          {item.product.category} / <span>{item.product.subcategory}</span>
                        </div>
                        {item.variant && (
                          <div className="mb-1"><span className="badge bg-info text-dark">Variant: {item.variant.name}</span></div>
                        )}
                        <div className="mb-1">
                          Qty: <span className="fw-bold">{item.quantity}</span>
                          <button className="btn btn-sm btn-outline-primary ms-2" onClick={() => handleEditQuantity(item.id, item.quantity + 1)}>+</button>
                          <button className="btn btn-sm btn-outline-primary ms-1" onClick={() => handleEditQuantity(item.id, Math.max(1, item.quantity - 1))}>-</button>
                        </div>
                        <div className="mb-1">Price: <span className="fw-bold">${item.price}</span></div>
                        <div className="mb-1">Total: <span className="fw-bold">${item.total}</span></div>
                        <button className="btn btn-sm btn-outline-danger mt-2" onClick={() => handleRemove(item.id)}>Remove</button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
      <div className="mt-4 text-end">
        <h4>Total: <span className="fw-bold">${cartTotal}</span></h4>
        <button
          className="btn btn-primary mt-2"
          onClick={() => {
            if (!user) {
              // Gate checkout for guests: redirect to login
              navigate('/login');
            } else {
              navigate('/checkout');
            }
          }}
        >
          Proceed to Checkout
        </button>
      </div>
    </div>
  );
};

export default CartPage;
