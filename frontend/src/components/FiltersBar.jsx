import React from 'react';
import './FiltersBar.css';

export default function FiltersBar({ filters, onChange }) {
  return (
    <div className="filters-bar" role="region" aria-label="Product filters">
      <input
        className="form-control form-control-sm"
        style={{ minWidth: 220 }}
        name="q"
        value={filters.q}
        onChange={onChange}
        placeholder="Search products..."
      />
      <div className="d-flex align-items-center gap-1">
        <span className="text-muted small">Price</span>
        <input
          className="form-control form-control-sm price"
          name="min_price"
          value={filters.min_price}
          onChange={onChange}
          placeholder="Min"
        />
        <span className="text-muted small">-</span>
        <input
          className="form-control form-control-sm price"
          name="max_price"
          value={filters.max_price}
          onChange={onChange}
          placeholder="Max"
        />
      </div>
      <div className="form-check form-check-inline m-0">
        <input
          className="form-check-input"
          type="checkbox"
          id="in_stock"
          name="in_stock"
          checked={filters.in_stock}
          onChange={onChange}
        />
        <label className="form-check-label small" htmlFor="in_stock">In stock</label>
      </div>
      <select
        className="form-select form-select-sm"
        name="sort"
        value={filters.sort}
        onChange={onChange}
        style={{ minWidth: 180 }}
      >
        <option value="relevance">Sort: Relevance</option>
        <option value="price_asc">Price: Low to High</option>
        <option value="price_desc">Price: High to Low</option>
        <option value="name_asc">Name: A-Z</option>
      </select>
    </div>
  );
}
