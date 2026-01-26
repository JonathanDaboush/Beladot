from sqlalchemy import delete
## Removed ensure_sqlite_schema import; not needed for Postgres
from backend.persistance.base import get_sessionmaker

# Import models with FKs to product that should be cleared first
from backend.persistance.cart_item import CartItem
from backend.persistance.wishlist_item import WishlistItem
from backend.persistance.shipment_item import ShipmentItem
from backend.persistance.order_item import OrderItem
from backend.persistance.product_comment import ProductComment
from backend.persistance.product_variant_image import ProductVariantImage
from backend.persistance.product_image import ProductImage
from backend.persistance.product_review import ProductReview
from backend.persistance.product_rating import ProductRating
from backend.persistance.product_variant import ProductVariant
from backend.persistance.product import Product


def main() -> None:
    # No schema creation needed for Postgres
    Session = get_sessionmaker()
    with Session() as session:
        # Helper to try delete and skip if table doesn't exist
        def try_delete(model):
            try:
                session.execute(delete(model))
            except Exception as e:
                if 'does not exist' in str(e) or 'UndefinedTable' in str(e):
                    print(f"Skipping missing table: {getattr(model, '__tablename__', model)}")
                else:
                    raise

        # Delete dependents first to satisfy FKs
        try_delete(CartItem)
        try_delete(WishlistItem)
        try_delete(ShipmentItem)
        try_delete(OrderItem)
        try_delete(ProductComment)
        try_delete(ProductVariantImage)
        try_delete(ProductImage)
        try_delete(ProductReview)
        try_delete(ProductRating)
        try_delete(ProductVariant)
        try_delete(Product)
        session.commit()
    print("Purged all products and related records.")


if __name__ == "__main__":
    main()
