# Represents an image associated with a product
class ProductImage:
    def __init__(self, id, product_id, blob_id, alt_text, is_primary, sort_order):
        self.id = id # Unique identifier for the product image
        self.product_id = product_id # ID of the product this image belongs to
        self.blob_id = blob_id # Reference to the image file in storage
        self.alt_text = alt_text # Alternative text for accessibility
        self.is_primary = is_primary # Whether this is the primary image for the product
        self.sort_order = sort_order # Order in which this image appears among product images