# Represents a physical shipment of products to customer with tracking information.
# One order can have multiple shipments if items ship separately (backordered items, different warehouses).
class Shipment:
    def __init__(self, id, order_id, tracking_number, carrier, status, label_blob_id, cost_cents, shipped_at, estimated_delivery, delivered_at, notes, created_at, updated_at):
        self.id = id  # Unique shipment identifier
        self.order_id = order_id  # Links to Order being shipped
        self.tracking_number = tracking_number  # Tracking number from carrier (e.g., "1Z999AA10123456784" for UPS)
        self.carrier = carrier  # Shipping company: "ups", "fedex", "usps", "dhl", "local_courier"
        self.status = status  # Shipment state: "pending", "label_created", "picked_up", "in_transit", "out_for_delivery", "delivered", "exception"
        self.label_blob_id = label_blob_id  # Links to Blob containing printable shipping label PDF
        self.cost_cents = cost_cents  # Actual shipping cost charged by carrier (in cents, may differ from what customer paid)
        self.shipped_at = shipped_at  # When package was picked up by carrier or dropped off
        self.estimated_delivery = estimated_delivery  # Expected delivery date provided by carrier
        self.delivered_at = delivered_at  # When package was actually delivered (null if not yet delivered)
        self.notes = notes  # Additional shipment info (e.g., "Signature required", "Left at front door")
        self.created_at = created_at  # When shipment record was created
        self.updated_at = updated_at  # When shipment status last changed