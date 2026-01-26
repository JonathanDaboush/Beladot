import React, { useEffect, useRef, useState } from 'react';
import './VisualCategoryNavigation.css';

export default function VisualCategoryNavigation({
  activeCategoryId,
  activeSubcategoryId,
  onSelectCategory,
  onSelectSubcategory,
}) {
  const [categories, setCategories] = useState([]);
  const [openIdx, setOpenIdx] = useState(null);
  const hoverTimerRef = useRef(null);
  const apiBase = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch('/api/categories');
        const data = await res.json();
        if (mounted) setCategories(Array.isArray(data.categories) ? data.categories : []);
      } catch (e) {
        if (mounted) setCategories([]);
      }
    })();
    return () => { mounted = false; if (hoverTimerRef.current) clearTimeout(hoverTimerRef.current); };
  }, []);

  const handleEnter = (idx) => {
    if (hoverTimerRef.current) clearTimeout(hoverTimerRef.current);
    setOpenIdx(idx);
  };
  const handleLeave = (idx) => {
    if (hoverTimerRef.current) clearTimeout(hoverTimerRef.current);
    hoverTimerRef.current = setTimeout(() => {
      setOpenIdx((prev) => (prev === idx ? null : prev));
    }, 120);
  };

  const clickCategory = (cat) => {
    setOpenIdx(null);
    onSelectCategory?.(cat);
  };
  const clickSubcategory = (cat, sub) => {
    setOpenIdx(null);
    onSelectSubcategory?.(cat, sub);
  };

  const fullUrl = (u) => {
    if (!u) return 'none';
    if (u.startsWith('http://') || u.startsWith('https://')) return `url(${u})`;
    return `url(${apiBase}${u})`;
  };

  return (
    <nav className="vcat-nav" aria-label="Visual category navigation">
      <ul className="vcat-row">
        {categories.map((cat, idx) => (
          <li
            key={cat.category_id}
            className={`vcat-item ${openIdx === idx ? 'open' : ''}`}
            onMouseEnter={() => handleEnter(idx)}
            onMouseLeave={() => handleLeave(idx)}
          >
            <button
              className={`vcat-tile ${String(activeCategoryId) === String(cat.category_id) && !activeSubcategoryId ? 'active' : ''}`}
              onClick={() => clickCategory(cat)}
              aria-label={cat.name}
              style={{
                backgroundImage: fullUrl(cat.image_url),
              }}
            >
              <span className="vcat-overlay" />
              <span className="vcat-text">{cat.name}</span>
            </button>
            {Array.isArray(cat.subcategories) && cat.subcategories.length > 0 && (
              <div className="vcat-dropdown">
                <ul className="vsub-grid">
                  {cat.subcategories.map((sub) => (
                    <li key={sub.subcategory_id}>
                      <button
                        className={`vsub-tile ${String(activeSubcategoryId) === String(sub.subcategory_id) ? 'active' : ''}`}
                        onClick={() => clickSubcategory(cat, sub)}
                        aria-label={sub.name}
                        style={{
                          backgroundImage: fullUrl(sub.image_url),
                        }}
                      >
                        <span className="vcat-overlay" />
                        <span className="vcat-text small">{sub.name}</span>
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
