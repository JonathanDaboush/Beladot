import React, { useEffect, useMemo, useState } from 'react';
import { useLocation } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import FiltersBar from '../components/FiltersBar';
import VisualCategoryNavigation from '../components/VisualCategoryNavigation';

function useQuery() {
  const { search } = useLocation();
  return useMemo(() => new URLSearchParams(search), [search]);
}

export default function BrowsePage({ forceSubcategoryId }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    q: '',
    category_id: '',
    subcategory_id: '',
    min_price: '',
    max_price: '',
    in_stock: false,
    sort: 'relevance',
  });

  const query = useQuery();
  const subcategoryParam = forceSubcategoryId || query.get('subcategory_id') || '';
  const categoryParam = query.get('category_id') || '';

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const res = await fetch('/api/v1/catalog/products');
        const data = await res.json();
        setItems(Array.isArray(data.items) ? data.items : []);
        setError(null);
      } catch (e) {
        setError('Failed to load products');
        setItems([]);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  useEffect(() => {
    setFilters((f) => ({
      ...f,
      category_id: categoryParam || '',
      subcategory_id: subcategoryParam || '',
    }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [categoryParam, subcategoryParam]);

  const filtered = useMemo(() => {
    let out = items.slice();
    const q = filters.q.trim().toLowerCase();
    if (q) {
      out = out.filter((p) =>
        (p.name || '').toLowerCase().includes(q) || (p.description || '').toLowerCase().includes(q)
      );
    }
    if (filters.category_id) {
      out = out.filter((p) => String(p.category_id) === String(filters.category_id));
    }
    if (filters.subcategory_id) {
      out = out.filter((p) => String(p.subcategory_id) === String(filters.subcategory_id));
    }
    const min = parseFloat(filters.min_price);
    const max = parseFloat(filters.max_price);
    if (!isNaN(min)) out = out.filter((p) => (p.price ?? 0) >= min);
    if (!isNaN(max)) out = out.filter((p) => (p.price ?? 0) <= max);
    if (filters.in_stock) {
      // Without stock info, approximate by price presence
      out = out.filter((p) => (p.price ?? 0) > 0);
    }
    switch (filters.sort) {
      case 'price_asc':
        out.sort((a, b) => (a.price ?? 0) - (b.price ?? 0));
        break;
      case 'price_desc':
        out.sort((a, b) => (b.price ?? 0) - (a.price ?? 0));
        break;
      case 'name_asc':
        out.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
        break;
      default:
        break;
    }
    return out;
  }, [items, filters]);

  const onChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFilters((f) => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
  };

  const selectCategory = (cat) => {
    setFilters((f) => ({ ...f, category_id: cat?.category_id || '', subcategory_id: '' }));
  };
  const selectSubcategory = (cat, sub) => {
    setFilters((f) => ({ ...f, category_id: cat?.category_id || '', subcategory_id: sub?.subcategory_id || '' }));
  };

  return (
    <div className="container py-3">
      <PageHeader title="Browse Products" subtitle="Filter by category, price and more" />
      <VisualCategoryNavigation
        activeCategoryId={filters.category_id}
        activeSubcategoryId={filters.subcategory_id}
        onSelectCategory={selectCategory}
        onSelectSubcategory={selectSubcategory}
      />
      <FiltersBar filters={filters} onChange={onChange} />
      {loading && <div>Loading products...</div>}
      {error && <div className="alert alert-danger">{error}</div>}
      {!loading && !error && (
        <div className="row row-cols-1 row-cols-sm-2 row-cols-lg-3 g-3">
          {filtered.map((p) => (
            <div key={p.id} className="col">
              <div className="card h-100">
                {p.image_url && (
                  <img
                    src={(p.image_url.startsWith('http') ? p.image_url : `${process.env.REACT_APP_API_BASE || 'http://localhost:8000'}${p.image_url}`)}
                    alt={p.name}
                    className="card-img-top"
                    style={{ objectFit: 'cover', height: 160 }}
                  />
                )}
                <div className="card-body">
                  <div className="fw-bold mb-1">{p.name}</div>
                  <div className="text-muted small mb-1">{p.category}{p.subcategory ? ` / ${p.subcategory}` : ''}</div>
                  <div className="fw-semibold">${p.price ?? 0}</div>
                </div>
                <div className="card-footer bg-white">
                  <a className="btn btn-sm btn-outline-primary" href={`/product/${p.id}`}>View</a>
                </div>
              </div>
            </div>
          ))}
          {filtered.length === 0 && (
            <div className="col-12">
              <div className="alert alert-secondary">No products match your filters.</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
