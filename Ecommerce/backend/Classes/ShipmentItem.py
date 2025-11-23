# Represents which OrderItems are included in a specific shipment and in what quantities.
# Needed because orders can ship in multiple boxes or some items may ship separately.
class ShipmentItem:
    def __init__(self, id, shipment_id, order_item_id, quantity):
        self.id = id  # Unique shipment item identifier
        self.shipment_id = shipment_id  # Links to parent Shipment
        self.order_item_id = order_item_id  # Links to OrderItem being shipped in this package
        self.quantity = quantity  # How many units of this item are in this shipment (may be less than ordered if partial shipment)
