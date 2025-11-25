import re
import os

class Address:
    def __init__(self, id, user_id, address_line1, address_line2, city, state, country, postal_code, is_default):
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
        return True