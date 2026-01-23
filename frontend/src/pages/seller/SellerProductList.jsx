// Moved from src/seller
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SellerProductCard from './SellerProductCard';
import Button from '../../components/Button';
import './SellerProductList.css';

const PAGE_SIZES = [25, 50, 75];

export default function SellerProductList() {
  const [products, setProducts] = useState([]);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(PAGE_SIZES[0]);
  const [filters, setFilters] = useState({});
  const [total, setTotal] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    // TODO: Replace with real API call
    // fetch seller products with filters, page, pageSize
    // setProducts(response.data)
    // setTotal(response.total)
  }, [page, pageSize, filters]);

  return (
    <div className="seller-product-list">
      <PageHeader title="Products" subtitle="Manage your listings and availability" action={<Button kind="primary" onClick={() => navigate('/seller/products/add')}>Create Product</Button>} />
      <div className="filters-panel">
        {/* TODO: Render filter controls here */}
      </div>
      <div className="products-grid">
        {products.map(product => (
          <SellerProductCard key={product.product_id} product={product} onClick={() => navigate(`/seller/products/${product.product_id}`)} />
        ))}
      </div>
      <div className="pagination-controls">
        <label>Page size: </label>
        <select value={pageSize} onChange={e => setPageSize(Number(e.target.value))}>
          {PAGE_SIZES.map(size => <option key={size} value={size}>{size}</option>)}
        </select>
        {/* TODO: Add page navigation controls */}
      </div>
    </div>
  );
}
