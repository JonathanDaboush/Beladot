import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './CategoryPage.css';

const CategoryPage = () => {
  const { id } = useParams();
  const [category, setCategory] = useState(null);
  const [subcategories, setSubcategories] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`/api/category/${id}`)
      .then(res => res.json())
      .then(data => {
        setCategory(data.category);
        setSubcategories(data.subcategories || []);
      });
  }, [id]);

  if (!category) return <div className="category-loading">Loading...</div>;

  return (
    <div className="category-page">
      <img
        src={(category.image_url && (category.image_url.startsWith('http') ? category.image_url : `${process.env.REACT_APP_API_BASE || 'http://localhost:8000'}${category.image_url}`))}
        alt={category.name}
        className="category-image"
      />
      <h2>{category.name}</h2>
      <div className="subcategory-grid">
        {subcategories.map(sub => (
          <div key={sub.subcategory_id} className="subcategory-tile" onClick={() => navigate(`/subcategory/${sub.subcategory_id}`)}>
            <img
              src={(sub.image_url && (sub.image_url.startsWith('http') ? sub.image_url : `${process.env.REACT_APP_API_BASE || 'http://localhost:8000'}${sub.image_url}`))}
              alt={sub.name}
              className="subcategory-image"
            />
            <div className="subcategory-name">{sub.name}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CategoryPage;
