import requests
"""
Currency Conversion Service
===========================

Handles multi-currency support and exchange rates.

Business rules enforced at service layer

Dependencies:
- ExchangeRateProvider
    - CurrencyRepository

Author: Jonathan Daboush
Version: 2.0.0
"""


class CurrencyConversionService:
    """
    Service to convert currency amounts using a free public API.
    Focused on USD but supports any currency pair.
    """
    API_URL = "https://api.exchangerate.host/convert"

    def convert(self, from_currency: str, to_currency: str, amount: float) -> float:
        """
        Convert an amount from one currency to another using exchangerate.host.
        Args:
            from_currency: The source currency code (e.g., 'USD')
            to_currency: The target currency code (e.g., 'EUR')
            amount: The amount to convert
        Returns:
            The converted amount as a float (or None if failed)
        """
        params = {
            'from': from_currency.upper(),
            'to': to_currency.upper(),
            'amount': amount
        }
        try:
            response = requests.get(self.API_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get('result')
        except Exception as e:
            print(f"Currency conversion error: {e}")
            return None
