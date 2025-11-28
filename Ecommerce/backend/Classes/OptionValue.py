class OptionValue:
    """
    Domain model for option values (e.g., Red, Blue for Color).
    """
    def __init__(self, id, category_id, value, description=None):
        self.id = id
        self.category_id = category_id
        self.value = value
        self.description = description

    def __repr__(self):
        return f"<OptionValue(id={self.id}, category_id={self.category_id}, value={self.value})>"
