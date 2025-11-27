class ProductImage:
    """
    Domain model representing a product image with ordering and accessibility features.
    
    This class manages product image metadata, including display order, primary image
    designation, and accessibility text. Images stored as Blobs, this tracks the association
    to products.
    
    Key Responsibilities:
        - Link products to image blobs
        - Designate primary image for product listings
        - Control image display order
        - Provide accessibility text (alt text)
        - Generate image URLs
    
    Design Patterns:
        - Value Object within Product aggregate
        - Owned entity (lifecycle controlled by Product)
    
    Design Notes:
        - Actual image data stored in Blob (external storage)
        - sort_order determines display sequence
        - is_primary flag marks main product image
        - alt_text critical for SEO and accessibility
        - This is a domain object; persistence handled by ProductImageRepository
    """
    def __init__(self, id, product_id, blob_id, alt_text, is_primary, sort_order):
        """
        Initialize a ProductImage domain object.
        
        Args:
            id: Unique identifier (None for new images before persistence)
            product_id: Foreign key to the product
            blob_id: Foreign key to the image blob
            alt_text: Accessibility text for screen readers and SEO
            is_primary: Whether this is the primary image for the product
            sort_order: Display order (lower numbers appear first)
        """
        self.id = id
        self.product_id = product_id
        self.blob_id = blob_id
        self.alt_text = alt_text
        self.is_primary = is_primary
        self.sort_order = sort_order
    
    def get_url(self) -> str:
        """
        Generate the URL for accessing this product image.
        
        Returns:
            str: Image URL (blob-based or default placeholder)
            
        Design Notes:
            - Returns default image if no blob_id
            - Production should use CDN URLs from blob service
            - Current implementation assumes static file serving
        """
        if not self.blob_id:
            return '/static/images/default-product.png'
        
        return f'/static/images/products/{self.blob_id}'