/**
 * Guest Cart
 *
 * Stores cart items for non-signed-in users using localStorage
 * and a lightweight cookie flag. No backend/database persistence.
 */

const STORAGE_KEY = 'guestCart';
const COOKIE_NAME = 'guest_cart_present';

function setCookieFlag() {
  try {
    const maxAgeDays = 30;
    const maxAgeSeconds = maxAgeDays * 24 * 60 * 60;
    document.cookie = `${COOKIE_NAME}=true; path=/; max-age=${maxAgeSeconds}`;
  } catch (_) {
    // Ignore cookie failures (e.g., non-browser tests)
  }
}

function readCart() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const data = JSON.parse(raw);
    if (Array.isArray(data)) return data;
    return [];
  } catch (_) {
    return [];
  }
}

function writeCart(items) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    setCookieFlag();
  } catch (_) {
    // ignore
  }
}

function getItemKey(product, variant) {
  const pid = product?.id ?? product?.product_id ?? product?.productId;
  const vid = variant?.id ?? variant?.variant_id ?? variant?.variantId;
  return vid || pid;
}

export function getGuestCart() {
  return readCart();
}

export function clearGuestCart() {
  writeCart([]);
}

export function addGuestCartItem(product, variant, quantity = 1) {
  const items = readCart();
  const key = getItemKey(product, variant);
  const existingIdx = items.findIndex((it) => it.id === key);

  const base = {
    id: key,
    product: {
      id: product?.id ?? product?.product_id ?? product?.productId,
      name: product?.name ?? product?.title ?? 'Product',
      image_url: product?.image_url ?? product?.image ?? null,
      category: product?.category ?? product?.category_name ?? null,
      subcategory: product?.subcategory ?? product?.subcategory_name ?? null,
      price: product?.price ?? 0,
    },
    variant: variant
      ? {
          id: variant?.id ?? variant?.variant_id ?? variant?.variantId,
          name: variant?.name ?? variant?.title ?? null,
          image_url: variant?.image_url ?? variant?.image ?? null,
          price: variant?.price ?? null,
        }
      : null,
    quantity: quantity,
  };

  if (existingIdx >= 0) {
    const updated = { ...items[existingIdx] };
    updated.quantity = Math.max(1, updated.quantity + quantity);
    items[existingIdx] = updated;
  } else {
    items.push(base);
  }

  writeCart(items);
  return items;
}

export function updateGuestCartItem(itemId, newQty) {
  const items = readCart();
  const idx = items.findIndex((it) => it.id === itemId);
  if (idx >= 0) {
    const qty = Math.max(1, Number(newQty) || 1);
    items[idx] = { ...items[idx], quantity: qty };
    writeCart(items);
  }
  return items;
}

export function removeGuestCartItem(itemId) {
  const items = readCart();
  const filtered = items.filter((it) => it.id !== itemId);
  writeCart(filtered);
  return filtered;
}

export function mapGuestItemsForDisplay(items) {
  return items.map((it) => {
    const unitPrice = it.variant?.price ?? it.product.price ?? 0;
    const total = unitPrice * it.quantity;
    return {
      id: it.id,
      product: {
        name: it.product.name,
        image_url: it.variant?.image_url || it.product.image_url,
        category: it.product.category,
        subcategory: it.product.subcategory,
      },
      variant: it.variant
        ? { name: it.variant.name, image_url: it.variant.image_url }
        : null,
      quantity: it.quantity,
      price: unitPrice,
      total,
    };
  });
}
