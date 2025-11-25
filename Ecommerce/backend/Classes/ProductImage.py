from typing import Optional
import os

class ProductImage:
    def __init__(self, id, product_id, blob_id, alt_text, is_primary, sort_order):
        self.id = id
        self.product_id = product_id
        self.blob_id = blob_id
        self.alt_text = alt_text
        self.is_primary = is_primary
        self.sort_order = sort_order
        self._blob = None
        self._url_cache = None
    
    def get_url(self, blob_repository=None, ttl_seconds: int = 300) -> str:
        if self._url_cache:
            return self._url_cache
        
        if not self.blob_id:
            fallback_url = os.getenv('DEFAULT_PRODUCT_IMAGE_URL', '/static/default-product.png')
            return fallback_url
        
        if blob_repository:
            try:
                blob = blob_repository.get_by_id(self.blob_id)
                if blob and hasattr(blob, 'get_signed_url'):
                    url = blob.get_signed_url(ttl_seconds)
                    self._url_cache = url
                    return url
            except Exception as e:
                pass
        
        cdn_base = os.getenv('CDN_BASE_URL', '')
        if cdn_base:
            return f"{cdn_base}/images/{self.blob_id}"
        
        return f"/api/blobs/{self.blob_id}"