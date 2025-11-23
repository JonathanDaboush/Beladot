# Represents a customer review/rating for a product.
# Reviews help other customers make purchase decisions and provide feedback to sellers.
class Review:
    def __init__(self, id, product_id, user_id, rating, title, comment, is_verified_purchase, created_at, updated_at):
        self.id = id  # Unique review identifier
        self.product_id = product_id  # Links to Product being reviewed
        self.user_id = user_id  # Links to User who wrote the review
        self.rating = rating  # Star rating (typically 1-5 scale)
        self.title = title  # Short review headline (e.g., "Great quality!", "Disappointing purchase")
        self.comment = comment  # Detailed review text with customer's thoughts and experience
        self.is_verified_purchase = is_verified_purchase  # Whether reviewer actually bought this product (displays "Verified Purchase" badge)
        self.created_at = created_at  # When review was posted
        self.updated_at = updated_at  # When review was last edited by customer
