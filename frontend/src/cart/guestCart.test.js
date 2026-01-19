import {
  getGuestCart,
  clearGuestCart,
  addGuestCartItem,
  updateGuestCartItem,
  removeGuestCartItem,
  mapGuestItemsForDisplay,
} from './guestCart';

describe('guestCart', () => {
  beforeEach(() => {
    clearGuestCart();
    // reset cookie
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: '',
    });
  });

  test('adds product without variant and stores in localStorage', () => {
    const prod = { id: 101, name: 'Widget', price: 9.99, image_url: '/p.png', category: 'Cat', subcategory: 'Sub' };
    addGuestCartItem(prod, null, 2);
    const cart = getGuestCart();
    expect(cart).toHaveLength(1);
    expect(cart[0].id).toBe(101);
    expect(cart[0].quantity).toBe(2);
    expect(document.cookie).toMatch(/guest_cart_present=true/);
  });

  test('adds product with variant and increments quantity if same key', () => {
    const prod = { id: 5, name: 'Gizmo', price: 4 };
    const variant = { id: 5001, name: 'Red', price: 5 };
    addGuestCartItem(prod, variant, 1);
    addGuestCartItem(prod, variant, 3);
    const cart = getGuestCart();
    expect(cart).toHaveLength(1);
    expect(cart[0].id).toBe(5001); // variant key dominates
    expect(cart[0].quantity).toBe(4);
  });

  test('update quantity and remove item', () => {
    const prod = { id: 7, name: 'Thing', price: 2 };
    addGuestCartItem(prod, null, 1);
    let cart = getGuestCart();
    const id = cart[0].id;
    updateGuestCartItem(id, 5);
    cart = getGuestCart();
    expect(cart[0].quantity).toBe(5);
    removeGuestCartItem(id);
    cart = getGuestCart();
    expect(cart).toHaveLength(0);
  });

  test('maps items for display with totals', () => {
    const prod = { id: 9, name: 'Prod', price: 3, image_url: '/p.png', category: 'C', subcategory: 'S' };
    const variant = { id: 900, name: 'Blue', price: 4, image_url: '/v.png' };
    addGuestCartItem(prod, variant, 2);
    const mapped = mapGuestItemsForDisplay(getGuestCart());
    expect(mapped[0].price).toBe(4);
    expect(mapped[0].total).toBe(8);
    expect(mapped[0].product.name).toBe('Prod');
  });
});
