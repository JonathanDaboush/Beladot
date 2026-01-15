"""
shipment_address.py

Model for shipment address entity.
Represents the address details for a shipment, including recipient and location.
"""

class ShipmentAddress:
    def __init__(self, shipment_address_id, shipment_id, recipient_name, address_line_1, address_line_2, city, state_province, postal_code, country, phone_number):
        """
        Initialize ShipmentAddress.
        Args:
            shipment_address_id (int): Unique identifier for the shipment address.
            shipment_id (int): Associated shipment ID.
            recipient_name (str): Name of the recipient.
            address_line_1 (str): First line of the address.
            address_line_2 (str): Second line of the address.
            city (str): City name.
            state_province (str): State or province.
            postal_code (str): Postal code.
            country (str): Country name.
            phone_number (str): Recipient's phone number.
        """
        self.shipment_address_id = shipment_address_id
        self.shipment_id = shipment_id
        self.recipient_name = recipient_name
        self.address_line_1 = address_line_1
        self.address_line_2 = address_line_2
        self.city = city
        self.state_province = state_province
        self.postal_code = postal_code
        self.country = country
        self.phone_number = phone_number
