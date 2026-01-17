import React, { useState } from 'react';
import { editWishlistItemQuantity, removeWishlistItem } from '../api/wishlist';
import DecisionFrame from '../components/DecisionFrame';
import useWishlistItems from '../hooks/useWishlistItems';

const WishlistPage = () => {
  const { data: wishlistItems = [], loading, error } = useWishlistItems();
  const [decisionMode, setDecisionMode] = useState(false);
  const [decisionType, setDecisionType] = useState('');
  const [selectedItem, setSelectedItem] = useState(null);
  const [newQty, setNewQty] = useState(1);
  const [preview, setPreview] = useState('');

  const getPreview = async (type, item, qty) => {
    if (!item) return '';
    if (type === 'edit') {
      return `Change quantity of ${item.product.name}${item.variant ? ' (' + item.variant.name + ')' : ''} to ${qty}`;
    }
    if (type === 'remove') {
      return `Remove ${item.product.name}${item.variant ? ' (' + item.variant.name + ')' : ''} from wishlist.`;
    }
    return '';
  };

  const openDecision = async (type, item) => {
    setDecisionType(type);
    setSelectedItem(item);
    setNewQty(item.quantity);
    setPreview(await getPreview(type, item, item.quantity));
    setDecisionMode(true);
  };

  const handleConfirm = async () => {
    try {
      if (decisionType === 'edit' && selectedItem) {
        await editWishlistItemQuantity(selectedItem.id, newQty);
      } else if (decisionType === 'remove' && selectedItem) {
        await removeWishlistItem(selectedItem.id);
      }
      setDecisionMode(false);
      setSelectedItem(null);
      setPreview('');
    } catch (e) {
      // surface minimal error state
      console.error(e);
    }
  };

  return (
    <div className="container py-4">
      <h2 className="mb-4">Your Wishlist</h2>
      {loading ? (
        <div className="alert alert-info">Loading...</div>
      ) : error ? (
        <div className="alert alert-danger">{error}</div>
      ) : (
        <div className="row g-3">
          {wishlistItems.length === 0 ? (
            <div className="col-12">
              <div className="alert alert-secondary text-center">Your wishlist is empty.</div>
            </div>
          ) : (
            wishlistItems.map(item => (
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
                        <div className="mb-2">
                          Qty: <span className="fw-bold">{item.quantity}</span>
                        </div>
                        <div className="d-flex gap-2">
                          <button className="btn btn-sm btn-outline-primary" onClick={() => openDecision('edit', item)}>Edit</button>
                          <button className="btn btn-sm btn-outline-danger" onClick={() => openDecision('remove', item)}>Remove</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {decisionMode && (
        <DecisionFrame
          open={decisionMode}
          title={decisionType === 'edit' ? 'Edit Quantity' : 'Remove Item'}
          preview={preview}
          onCancel={() => setDecisionMode(false)}
          onConfirm={handleConfirm}
        >
          {decisionType === 'edit' && selectedItem && (
            <div>
              <div className="mb-2">Edit quantity for <b>{selectedItem.product.name}{selectedItem.variant ? ' (' + selectedItem.variant.name + ')' : ''}</b></div>
              <input
                type="number"
                min={1}
                className="form-control w-50"
                value={newQty}
                onChange={async e => {
                  const val = Number(e.target.value);
                  setNewQty(val);
                  setPreview(await getPreview('edit', selectedItem, val));
                }}
              />
            </div>
          )}
          {decisionType === 'remove' && selectedItem && (
            <div>Are you sure you want to remove <b>{selectedItem.product.name}{selectedItem.variant ? ' (' + selectedItem.variant.name + ')' : ''}</b> from your wishlist?</div>
          )}
        </DecisionFrame>
      )}
    </div>
  );
};

export default WishlistPage;
