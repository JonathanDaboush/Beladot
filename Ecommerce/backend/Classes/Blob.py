from typing import IO, Optional
import os
from datetime import datetime, timedelta

class Blob:
    def __init__(self, id, storage_key, filename, content_type, size_bytes, checksum, storage_provider, created_at):
        self.id = id
        self.storage_key = storage_key
        self.filename = filename
        self.content_type = content_type
        self.size_bytes = size_bytes
        self.checksum = checksum
        self.storage_provider = storage_provider
        self.created_at = created_at
    
    def get_signed_url(self, ttl_seconds: int = 300, storage_service=None) -> str:
        if not storage_service:
            cdn_base = os.getenv('CDN_BASE_URL', '')
            if cdn_base:
                return f"{cdn_base}/{self.storage_key}"
            return f"/api/blobs/{self.id}/download"
        
        try:
            if self.storage_provider == "s3":
                return storage_service.generate_s3_signed_url(
                    key=self.storage_key,
                    expires_in=ttl_seconds
                )
            elif self.storage_provider == "azure":
                return storage_service.generate_azure_sas_url(
                    blob_name=self.storage_key,
                    expiry=timedelta(seconds=ttl_seconds)
                )
            elif self.storage_provider == "local":
                return f"/api/blobs/{self.id}/download"
            else:
                return storage_service.generate_signed_url(
                    key=self.storage_key,
                    ttl=ttl_seconds
                )
        except Exception as e:
            return f"/api/blobs/{self.id}/download"
    
    def open_stream(self, storage_service=None) -> Optional[IO]:
        if not storage_service:
            return None
        
        try:
            if self.storage_provider == "s3":
                return storage_service.get_s3_stream(self.storage_key)
            elif self.storage_provider == "azure":
                return storage_service.get_azure_stream(self.storage_key)
            elif self.storage_provider == "local":
                local_path = os.path.join(os.getenv('LOCAL_STORAGE_PATH', '/tmp/blobs'), self.storage_key)
                return open(local_path, 'rb')
            else:
                return storage_service.get_stream(self.storage_key)
        except Exception as e:
            return None