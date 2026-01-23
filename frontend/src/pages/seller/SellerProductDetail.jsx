// Moved from src/seller
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './SellerProductDetail.css';
import Button from '../../components/Button';
import PageHeader from '../../components/PageHeader';
import ConfirmDialog from '../../components/ConfirmDialog';

export default function SellerProductDetail() {
  const { productId } = useParams();
  const [product, setProduct] = useState(null);
  const [comments, setComments] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    // TODO: Fetch product detail and comments by productId
    // setProduct(response.product)
    // setComments(response.comments)
  }, [productId]);

  const handleEdit = () => navigate(`/seller/products/${productId}/edit`);
  const [confirmProductOpen, setConfirmProductOpen] = useState(false);
  const [confirmVariantOpen, setConfirmVariantOpen] = useState(false);
  const [variantToArchive, setVariantToArchive] = useState(null);

  const handleSoftDelete = () => {
    setConfirmProductOpen(true);
  };
  const handleVariantDelete = (variantId) => {
    setVariantToArchive(variantId);
    setConfirmVariantOpen(true);
  };
  const handleCommentResponse = (commentId, response) => {
    // TODO: Call respond to comment API
  };

  if (!product) return <div>Loading...</div>;

  const totalStock = product.variants?.reduce((sum, v) => sum + (v.stock || 0), 0) || 0;

  return (
    <div className="seller-product-detail">
      <PageHeader title={product.name} subtitle="Manage product details, variants and comments" action={<Button kind="secondary" onClick={handleEdit}>Edit Product</Button>} />
      <img src={product.image_url} alt={product.name} />
      <p>{product.description}</p>
      <p>Price: ${product.price}</p>
      <p>Category: {product.category_name}</p>
      <p>Total Stock: {totalStock}</p>
      <Button kind="destructive" onClick={handleSoftDelete}>Archive Product</Button>
      <h3>Variants</h3>
      <ul>
        {product.variants?.map(variant => (
          <li key={variant.variant_id}>
            {variant.name} (Stock: {variant.stock})
            <Button kind="destructive" onClick={() => handleVariantDelete(variant.variant_id)}>Archive Variant</Button>
          </li>
        ))}
      </ul>
      <h3>User Comments</h3>
            <ConfirmDialog
              open={confirmProductOpen}
              title="Archive Product"
              message="Archiving hides the product from customers without deleting it. Proceed?"
              confirmLabel="Archive"
              cancelLabel="Cancel"
              onConfirm={() => { setConfirmProductOpen(false); /* TODO: Call archive product API */ }}
              onCancel={() => setConfirmProductOpen(false)}
            />
            <ConfirmDialog
              open={confirmVariantOpen}
              title="Archive Variant"
              message="Archiving hides the variant from customers without deleting it. Proceed?"
              confirmLabel="Archive"
              cancelLabel="Cancel"
              onConfirm={() => { setConfirmVariantOpen(false); /* TODO: Call archive variant API using variantToArchive */ setVariantToArchive(null); }}
              onCancel={() => { setConfirmVariantOpen(false); setVariantToArchive(null); }}
            />
      <ul>
        {comments.map(comment => (
          <li key={comment.comment_id}>
            <p>{comment.text}</p>
            <input type="text" placeholder="Respond..." onBlur={e => handleCommentResponse(comment.comment_id, e.target.value)} />
          </li>
        ))}
      </ul>
    </div>
  );
}
