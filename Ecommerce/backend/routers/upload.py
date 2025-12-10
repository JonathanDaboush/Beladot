"""
File Upload Routes
Handles image uploads for products
- Product image upload (multiple images)
- Image validation (format, size)
- Thumbnail generation
- Blob storage integration
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import os
import uuid
import shutil
from pathlib import Path
from PIL import Image
import io

from database import get_db
from schemas import MessageResponse
from Utilities.auth import get_current_active_user
from Utilities.rate_limiting import rate_limiter_moderate
from Models.User import UserRole

router = APIRouter(prefix="/api/upload", tags=["File Upload"])

# Configuration
UPLOAD_DIR = Path(os.getenv('UPLOAD_DIR', './uploads'))
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
THUMBNAIL_SIZE = (300, 300)

# Create upload directories
(UPLOAD_DIR / 'products').mkdir(parents=True, exist_ok=True)
(UPLOAD_DIR / 'products' / 'thumbnails').mkdir(parents=True, exist_ok=True)


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename preserving extension"""
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    return f"{uuid.uuid4()}.{ext}"


async def save_upload_file(upload_file: UploadFile, destination: Path):
    """Save uploaded file to disk"""
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()


def create_thumbnail(source_path: Path, thumbnail_path: Path, size: tuple = THUMBNAIL_SIZE):
    """Create thumbnail from image"""
    try:
        with Image.open(source_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, 'JPEG', quality=85)
        return True
    except Exception as e:
        print(f"Failed to create thumbnail: {e}")
        return False


@router.post("/product-image", dependencies=[Depends(rate_limiter_moderate)])
async def upload_product_image(
    product_id: str = Form(...),
    file: UploadFile = File(...),
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload product image (sellers can upload for their products, admins for any)
    Returns image URL and thumbnail URL
    """
    from Services.CatalogService import CatalogService
    from Models.ProductImage import ProductImage
    from sqlalchemy import select
    
    # Check file type
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Reset file pointer
    await file.seek(0)
    
    # Verify product ownership
    catalog_service = CatalogService(db)
    product = await catalog_service.get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Authorization: Seller can upload for their products, Admin for any
    if current_user.role == UserRole.SELLER:
        if product.seller_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only upload images for your own products"
            )
    elif current_user.role not in [UserRole.ADMIN, UserRole.SELLER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers and admins can upload product images"
        )
    
    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename)
    file_path = UPLOAD_DIR / 'products' / unique_filename
    thumbnail_path = UPLOAD_DIR / 'products' / 'thumbnails' / unique_filename
    
    # Save original image
    await save_upload_file(file, file_path)
    
    # Create thumbnail
    create_thumbnail(file_path, thumbnail_path)
    
    # Save to database
    product_image = ProductImage(
        product_id=product_id,
        image_url=f"/uploads/products/{unique_filename}",
        thumbnail_url=f"/uploads/products/thumbnails/{unique_filename}",
        is_primary=False  # Can be set to True later
    )
    db.add(product_image)
    await db.commit()
    await db.refresh(product_image)
    
    return {
        "id": product_image.id,
        "image_url": product_image.image_url,
        "thumbnail_url": product_image.thumbnail_url,
        "message": "Image uploaded successfully"
    }


@router.post("/product-images-bulk", dependencies=[Depends(rate_limiter_moderate)])
async def upload_product_images_bulk(
    product_id: str = Form(...),
    files: List[UploadFile] = File(...),
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload multiple product images at once
    Returns list of uploaded image URLs
    """
    from Services.CatalogService import CatalogService
    from Models.ProductImage import ProductImage
    
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 images per upload"
        )
    
    # Verify product ownership
    catalog_service = CatalogService(db)
    product = await catalog_service.get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Authorization check
    if current_user.role == UserRole.SELLER:
        if product.seller_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only upload images for your own products"
            )
    elif current_user.role not in [UserRole.ADMIN, UserRole.SELLER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers and admins can upload product images"
        )
    
    uploaded_images = []
    
    for file in files:
        # Validate each file
        if not is_allowed_file(file.filename):
            continue
        
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            continue
        
        await file.seek(0)
        
        # Generate unique filename
        unique_filename = generate_unique_filename(file.filename)
        file_path = UPLOAD_DIR / 'products' / unique_filename
        thumbnail_path = UPLOAD_DIR / 'products' / 'thumbnails' / unique_filename
        
        # Save original image
        await save_upload_file(file, file_path)
        
        # Create thumbnail
        create_thumbnail(file_path, thumbnail_path)
        
        # Save to database
        product_image = ProductImage(
            product_id=product_id,
            image_url=f"/uploads/products/{unique_filename}",
            thumbnail_url=f"/uploads/products/thumbnails/{unique_filename}",
            is_primary=(len(uploaded_images) == 0)  # First image is primary
        )
        db.add(product_image)
        
        uploaded_images.append({
            "image_url": product_image.image_url,
            "thumbnail_url": product_image.thumbnail_url
        })
    
    await db.commit()
    
    return {
        "uploaded_count": len(uploaded_images),
        "images": uploaded_images,
        "message": f"{len(uploaded_images)} images uploaded successfully"
    }


@router.delete("/product-image/{image_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def delete_product_image(
    image_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete product image (sellers can delete their product images, admins can delete any)"""
    from Models.ProductImage import ProductImage
    from Models.Product import Product
    from sqlalchemy import select
    
    # Get image
    result = await db.execute(
        select(ProductImage).where(ProductImage.id == image_id)
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Check product ownership
    result = await db.execute(
        select(Product).where(Product.id == image.product_id)
    )
    product = result.scalar_one_or_none()
    
    if current_user.role == UserRole.SELLER:
        if not product or product.seller_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete images for your own products"
            )
    elif current_user.role not in [UserRole.ADMIN, UserRole.SELLER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers and admins can delete product images"
        )
    
    # Delete physical files
    try:
        file_path = UPLOAD_DIR / 'products' / Path(image.image_url).name
        thumbnail_path = UPLOAD_DIR / 'products' / 'thumbnails' / Path(image.thumbnail_url).name
        
        if file_path.exists():
            file_path.unlink()
        if thumbnail_path.exists():
            thumbnail_path.unlink()
    except Exception as e:
        print(f"Failed to delete image files: {e}")
    
    # Delete from database
    await db.delete(image)
    await db.commit()
    
    return {"message": "Image deleted successfully"}


@router.put("/product-image/{image_id}/set-primary", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def set_primary_image(
    image_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Set image as primary product image"""
    from Models.ProductImage import ProductImage
    from Models.Product import Product
    from sqlalchemy import select, update
    
    # Get image
    result = await db.execute(
        select(ProductImage).where(ProductImage.id == image_id)
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Check product ownership
    result = await db.execute(
        select(Product).where(Product.id == image.product_id)
    )
    product = result.scalar_one_or_none()
    
    if current_user.role == UserRole.SELLER:
        if not product or product.seller_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only modify images for your own products"
            )
    elif current_user.role not in [UserRole.ADMIN, UserRole.SELLER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers and admins can modify product images"
        )
    
    # Unset all other images for this product
    await db.execute(
        update(ProductImage)
        .where(ProductImage.product_id == image.product_id)
        .values(is_primary=False)
    )
    
    # Set this image as primary
    image.is_primary = True
    await db.commit()
    
    return {"message": "Primary image updated successfully"}
