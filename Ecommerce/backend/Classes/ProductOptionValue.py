class ProductOptionValue:
    def __init__(self, id, product_id, option_value_id):
        self.id = id
        self.product_id = product_id
        self.option_value_id = option_value_id
    def __repr__(self):
        return f"<ProductOptionValue(id={self.id}, product_id={self.product_id}, option_value_id={self.option_value_id})>"
