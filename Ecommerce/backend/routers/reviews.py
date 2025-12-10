"""
Reviews Routes
Handles product reviews and ratings
- Create review
- List reviews for product
- Update review
- Delete review  
- Mark review as helpful
- Moderate reviews (admin/CS only)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel

from database import get_db
from Utilities.auth import get_current_active_user
from Utilities.rate_limiting import rate_limiter_moderate
from Models.User import UserRole

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


class CreateReviewRequest(BaseModel):
    product_id: str
    rating: int  # 1-5
    title: str
    comment: str


class UpdateReviewRequest(BaseModel):
    rating: Optional[int] = None
    title: Optional[str] = None
    comment: Optional[str] = None


@router.post("", dependencies=[Depends(rate_limiter_moderate)])
async def create_review(
    review_data: CreateReviewRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a product review (customers only, must have purchased product)"""
    from Models.Review import Review
    from Models.Order import Order
    from Models.OrderItem import OrderItem
    from Models.Product import Product
    from sqlalchemy import select, and_
    
    # Validate rating
    if not 1 <= review_data.rating <= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    # Check if product exists
    result = await db.execute(select(Product).where(Product.id == review_data.product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if user has purchased this product
    result = await db.execute(
        select(OrderItem)
        .join(Order)
        .where(
            and_(
                Order.user_id == current_user.id,
                OrderItem.product_id == review_data.product_id,
                Order.status == "delivered"  # Only delivered orders
            )
        )
    )
    order_item = result.scalar_one_or_none()
    
    if not order_item and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review products you have purchased"
        )
    
    # Check if user already reviewed this product
    result = await db.execute(
        select(Review).where(
            and_(
                Review.user_id == current_user.id,
                Review.product_id == review_data.product_id
            )
        )
    )
    existing_review = result.scalar_one_or_none()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this product"
        )
    
    # Create review
    review = Review(
        user_id=current_user.id,
        product_id=review_data.product_id,
        rating=review_data.rating,
        title=review_data.title,
        comment=review_data.comment
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    
    return {
        "id": review.id,
        "rating": review.rating,
        "title": review.title,
        "comment": review.comment,
        "created_at": review.created_at,
        "message": "Review created successfully"
    }


@router.get("/product/{product_id}", dependencies=[Depends(rate_limiter_moderate)])
async def get_product_reviews(
    product_id: str,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "helpful",  # helpful, recent, rating_high, rating_low
    min_rating: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get reviews for a product with filtering and sorting"""
    from Models.Review import Review
    from Models.User import User
    from sqlalchemy import select, func, desc
    
    # Build query
    query = select(Review, User).join(User).where(Review.product_id == product_id)
    
    # Apply filters
    if min_rating:
        query = query.where(Review.rating >= min_rating)
    
    # Apply sorting
    if sort_by == "helpful":
        query = query.order_by(desc(Review.helpful_count))
    elif sort_by == "recent":
        query = query.order_by(desc(Review.created_at))
    elif sort_by == "rating_high":
        query = query.order_by(desc(Review.rating))
    elif sort_by == "rating_low":
        query = query.order_by(Review.rating)
    
    # Add pagination
    query = query.limit(limit).offset(offset)
    
    # Execute query
    result = await db.execute(query)
    reviews_with_users = result.all()
    
    # Get rating summary
    summary_query = select(
        func.count(Review.id).label('total_reviews'),
        func.avg(Review.rating).label('average_rating'),
        func.sum(func.case((Review.rating == 5, 1), else_=0)).label('five_star'),
        func.sum(func.case((Review.rating == 4, 1), else_=0)).label('four_star'),
        func.sum(func.case((Review.rating == 3, 1), else_=0)).label('three_star'),
        func.sum(func.case((Review.rating == 2, 1), else_=0)).label('two_star'),
        func.sum(func.case((Review.rating == 1, 1), else_=0)).label('one_star')
    ).where(Review.product_id == product_id)
    
    summary_result = await db.execute(summary_query)
    summary = summary_result.one()
    
    # Format reviews
    reviews_list = [
        {
            "id": review.id,
            "rating": review.rating,
            "title": review.title,
            "comment": review.comment,
            "helpful_count": review.helpful_count or 0,
            "created_at": review.created_at,
            "user": {
                "name": f"{user.first_name} {user.last_name[0]}.",  # Privacy: show only first letter of last name
                "verified_purchase": True  # Assume verified if review exists
            }
        }
        for review, user in reviews_with_users
    ]
    
    return {
        "reviews": reviews_list,
        "summary": {
            "total_reviews": summary.total_reviews or 0,
            "average_rating": float(summary.average_rating) if summary.average_rating else 0,
            "rating_distribution": {
                "5": summary.five_star or 0,
                "4": summary.four_star or 0,
                "3": summary.three_star or 0,
                "2": summary.two_star or 0,
                "1": summary.one_star or 0
            }
        },
        "pagination": {
            "limit": limit,
            "offset": offset
        }
    }


@router.put("/{review_id}", dependencies=[Depends(rate_limiter_moderate)])
async def update_review(
    review_id: str,
    review_data: UpdateReviewRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user's own review"""
    from Models.Review import Review
    from sqlalchemy import select
    
    # Get review
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check ownership
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own reviews"
        )
    
    # Update fields
    if review_data.rating is not None:
        if not 1 <= review_data.rating <= 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )
        review.rating = review_data.rating
    
    if review_data.title is not None:
        review.title = review_data.title
    
    if review_data.comment is not None:
        review.comment = review_data.comment
    
    await db.commit()
    await db.refresh(review)
    
    return {
        "id": review.id,
        "rating": review.rating,
        "title": review.title,
        "comment": review.comment,
        "message": "Review updated successfully"
    }


@router.delete("/{review_id}", dependencies=[Depends(rate_limiter_moderate)])
async def delete_review(
    review_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete user's own review (or any review if admin/CS)"""
    from Models.Review import Review
    from sqlalchemy import select
    
    # Get review
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check ownership or admin/CS permission
    if review.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.CUSTOMER_SERVICE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews"
        )
    
    await db.delete(review)
    await db.commit()
    
    return {"message": "Review deleted successfully"}


@router.post("/{review_id}/helpful", dependencies=[Depends(rate_limiter_moderate)])
async def mark_review_helpful(
    review_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a review as helpful"""
    from Models.Review import Review
    from sqlalchemy import select
    
    # Get review
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Increment helpful count
    review.helpful_count = (review.helpful_count or 0) + 1
    await db.commit()
    
    return {
        "helpful_count": review.helpful_count,
        "message": "Marked as helpful"
    }
