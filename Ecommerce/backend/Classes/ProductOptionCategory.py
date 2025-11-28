class ProductOptionCategory:
    def __init__(self, id, product_id, option_category_id):
        self.id = id
        self.product_id = product_id
        self.option_category_id = option_category_id
    def __repr__(self):
        return f"<ProductOptionCategory(id={self.id}, product_id={self.product_id}, option_category_id={self.option_category_id})>"
