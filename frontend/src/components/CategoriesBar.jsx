import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './CategoriesBar.css';

export default function CategoriesBar() {
  const [categories, setCategories] = useState([]);
  const [openIdx, setOpenIdx] = useState(null);
  const hoverTimerRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch('/api/categories');
        const data = await res.json();
        if (mounted) setCategories(Array.isArray(data.categories) ? data.categories : []);
      } catch {
        if (mounted) setCategories([]);
      }
    })();
    return () => { 
      mounted = false; 
      if (hoverTimerRef.current) {
        clearTimeout(hoverTimerRef.current);
      }
    };
  }, []);

  const handleMouseEnter = (idx) => {
    if (hoverTimerRef.current) clearTimeout(hoverTimerRef.current);
    setOpenIdx(idx);
  };

  const handleMouseLeave = (idx) => {
    if (hoverTimerRef.current) clearTimeout(hoverTimerRef.current);
    hoverTimerRef.current = setTimeout(() => {
      setOpenIdx((prev) => (prev === idx ? null : prev));
    }, 120);
  };

  const navigateAndClose = (path) => {
    if (hoverTimerRef.current) clearTimeout(hoverTimerRef.current);
    setOpenIdx(null);
    navigate(path);
  };

  return (
    <nav className="categories-bar" aria-label="Shop categories">
      <ul className="cat-row">
        {categories.map((cat, idx) => (
          <li
            key={cat.category_id}
            className={`cat-item ${openIdx === idx ? 'open' : ''}`}
            onMouseEnter={() => handleMouseEnter(idx)}
            onMouseLeave={() => handleMouseLeave(idx)}
          >
            <button className="cat-btn" onClick={() => navigateAndClose(`/category/${cat.category_id}`)}>
              {cat.name}
            </button>
            {Array.isArray(cat.subcategories) && cat.subcategories.length > 0 && (
              <div className="cat-dropdown">
                <ul>
                  {cat.subcategories.map((sub) => (
                    <li key={sub.subcategory_id}>
                      <button
                        className="sub-btn"
                        onClick={() => navigateAndClose(`/subcategory/${sub.subcategory_id}`)}
                      >
                        {sub.name}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </li>
        ))}
      </ul>
    </nav>
  );
}
