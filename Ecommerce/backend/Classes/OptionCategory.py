class OptionCategory:
    """
    Domain model for product option categories (e.g., Color, Size).
    """
    def __init__(self, id, name, description=None):
        self.id = id
        self.name = name
        self.description = description

    def __repr__(self):
        return f"<OptionCategory(id={self.id}, name={self.name})>"
