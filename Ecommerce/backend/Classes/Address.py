import re
import os

class Address:
    """
    Domain model representing a physical mailing address with validation capabilities.
    
    This class handles address data management and validation, supporting multiple
    country formats with region-specific postal code validation. It provides formatting
    for shipping labels and integrates with external address verification services.
    
    Key Responsibilities:
        - Store and manage address components (street, city, state, country, postal code)
        - Validate addresses against format rules and country-specific standards
        - Format addresses for shipping labels in a standardized way
        - Support integration with external address verification APIs
        - Track validation errors for user feedback
    
    Validation Features:
        - ISO 3166-1 alpha-2 country code enforcement (e.g., US, CA, GB)
        - Country-specific postal code format validation (regex patterns)
        - Required field enforcement with length constraints
        - Optional external verification service integration (configurable via env)
    
    Design Notes:
        - Validation is performed in-place, modifying address fields (trimming, uppercasing)
        - Errors accumulate in validation_errors list for comprehensive feedback
        - External validation can be enabled via EXTERNAL_ADDRESS_VALIDATION_ENABLED env var
        - This is a domain object; persistence handled by AddressRepository
    """
    def __init__(self, id, user_id, address_line1, address_line2, city, state, country, postal_code, is_default):
        """
        Initialize an Address domain object.
        
        Args:
            id: Unique identifier (None for new addresses before persistence)
            user_id: Foreign key to the owning user
            address_line1: Primary street address (required)
            address_line2: Secondary address line (apartment, suite - optional)
            city: City name (required)
            state: State/province/region name (required)
            country: ISO 3166-1 alpha-2 country code (e.g., US, CA, GB) (required)
            postal_code: Postal/ZIP code in country-specific format (required)
            is_default: Whether this is the user's default shipping/billing address
        """
        self.id = id
        self.user_id = user_id
        self.address_line1 = address_line1
        self.address_line2 = address_line2
        self.city = city
        self.state = state
        self.country = country
        self.postal_code = postal_code
        self.is_default = is_default
        self.validation_errors = []
        
    def format_for_label(self) -> str:
        """
        Format the address for printing on a shipping label.
        
        Produces a multi-line string representation suitable for shipping labels,
        following standard address formatting conventions with city/state/postal
        on one line and country on its own line.
        
        Returns:
            str: Formatted address with newline separators, country in uppercase
            
        Format Example:
            123 Main Street
            Apt 4B
            New York, NY 10001
            US
        """
        lines = []
        
        if self.address_line1:
            lines.append(self.address_line1)
        
        if self.address_line2:
            lines.append(self.address_line2)
        
        city_line_parts = []
        if self.city:
            city_line_parts.append(self.city)
        if self.state:
            city_line_parts.append(self.state)
        if self.postal_code:
            city_line_parts.append(self.postal_code)
        
        if city_line_parts:
            if len(city_line_parts) == 3:
                lines.append(f"{city_line_parts[0]}, {city_line_parts[1]} {city_line_parts[2]}")
            else:
                lines.append(" ".join(city_line_parts))
        
        if self.country:
            lines.append(self.country.upper())
        
        return "\n".join(lines)
    
    def validate(self) -> bool:
        """
        Validate and normalize address fields according to business rules.
        
        Performs comprehensive validation including required fields, length constraints,
        country-specific postal code formats, and optional external verification.
        Modifies address fields in-place (trimming whitespace, uppercasing country code).
        
        Returns:
            bool: True if address is valid, False otherwise
            
        Side Effects:
            - Populates self.validation_errors list with error messages
            - Normalizes fields: trims whitespace, uppercases country code
            - May call external address verification service if enabled
            
        Validation Rules:
            - address_line1: required, max 255 characters
            - address_line2: optional, max 255 characters
            - city: required, max 100 characters
            - state: required, max 50 characters
            - country: required, exactly 2 characters (ISO code)
            - postal_code: required, max 20 characters, country-specific format
            
        Design Notes:
            - External validation controlled by EXTERNAL_ADDRESS_VALIDATION_ENABLED env var
            - Errors accumulate so users can fix all issues at once
            - Country-specific postal validation supports US, CA, GB, DE, FR, AU
        """
        self.validation_errors = []
        
        self.country = self.country.strip().upper() if self.country else None
        self.address_line1 = self.address_line1.strip() if self.address_line1 else None
        self.address_line2 = self.address_line2.strip() if self.address_line2 else None
        self.city = self.city.strip() if self.city else None
        self.state = self.state.strip() if self.state else None
        self.postal_code = self.postal_code.strip() if self.postal_code else None
        
        if not self.address_line1 or len(self.address_line1.strip()) == 0:
            self.validation_errors.append("address_line1 is required and cannot be empty")
        elif len(self.address_line1) > 255:
            self.validation_errors.append("address_line1 cannot exceed 255 characters")
        
        if self.address_line2 and len(self.address_line2) > 255:
            self.validation_errors.append("address_line2 cannot exceed 255 characters")
        
        if not self.city or len(self.city.strip()) == 0:
            self.validation_errors.append("city is required and cannot be empty")
        elif len(self.city) > 100:
            self.validation_errors.append("city cannot exceed 100 characters")
        
        if not self.state or len(self.state.strip()) == 0:
            self.validation_errors.append("state is required and cannot be empty")
        elif len(self.state) > 50:
            self.validation_errors.append("state cannot exceed 50 characters")
        
        if not self.country:
            self.validation_errors.append("country is required")
        elif len(self.country) != 2:
            self.validation_errors.append("country must be exactly 2 characters (ISO-2 code like US, CA, GB)")
        
        if not self.postal_code or len(self.postal_code.strip()) == 0:
            self.validation_errors.append("postal_code is required and cannot be empty")
        elif len(self.postal_code) > 20:
            self.validation_errors.append("postal_code cannot exceed 20 characters")
        elif self.country:
            if not self._validate_postal_code(self.country, self.postal_code):
                self.validation_errors.append(f"postal_code format invalid for country {self.country}")
        
        external_validation_enabled = os.getenv('EXTERNAL_ADDRESS_VALIDATION_ENABLED', 'false').lower() == 'true'
        if external_validation_enabled and not self.validation_errors:
            external_valid = self._call_external_validation()
            if external_valid is False:
                self.validation_errors.append("Address verification failed via external service")
        
        return len(self.validation_errors) == 0
    
    def _validate_postal_code(self, country: str, postal_code: str) -> bool:
        """
        Validate postal code format for specific countries using regex patterns.
        
        Args:
            country: ISO 3166-1 alpha-2 country code
            postal_code: Postal code to validate
            
        Returns:
            bool: True if postal code matches country format or no pattern defined
            
        Supported Patterns:
            - US: 12345 or 12345-6789
            - CA: A1A 1A1 or A1A1A1
            - GB: Various UK postcode formats
            - DE/FR: 5-digit codes
            - AU: 4-digit codes
            
        Design Notes:
            - Returns True for unsupported countries (permissive default)
            - Case-insensitive matching for flexibility
        """
        patterns = {
            'US': r'^\d{5}(-\d{4})?$',
            'CA': r'^[A-Z]\d[A-Z]\s?\d[A-Z]\d$',
            'GB': r'^[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}$',
            'DE': r'^\d{5}$',
            'FR': r'^\d{5}$',
            'AU': r'^\d{4}$',
        }
        
        pattern = patterns.get(country)
        if not pattern:
            return True
        
        return re.match(pattern, postal_code, re.IGNORECASE) is not None
    
    def _call_external_validation(self) -> bool:
        """
        Call external address verification service (stub implementation).
        
        Returns:
            bool: True if address verified (always True in this stub)
            
        Design Notes:
            - Placeholder for integration with services like USPS, Google Address Validation
            - Would typically make HTTP call to verification API
            - Should handle timeouts and failures gracefully
            - Currently returns True to avoid blocking valid addresses
        """
        return True