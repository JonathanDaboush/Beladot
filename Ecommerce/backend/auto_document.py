# Automated Documentation Script for Backend Files
# Run this to add professional docstrings to all remaining files

import os
import re
from pathlib import Path

# Base directory
BACKEND_DIR = r"c:\Users\USER\Documents\Beladot\Ecommerce\backend"

# Documentation templates
SERVICE_TEMPLATE = '''"""
{title}
{separator}

{description}

{business_rules}

Dependencies:
{dependencies}

Author: Jonathan Daboush
Version: 2.0.0
"""
'''

CLASS_TEMPLATE = '''    """
    {class_description}
    
    {details}
    """'''

METHOD_TEMPLATE = '''        """
        {method_description}
        
        Args:
            {args}
            
        Returns:
            {returns}
            
        {raises}
        
        Example:
            {example}
        """'''

def add_module_docstring(filepath, title, description, business_rules="", dependencies=""):
    """Add module-level docstring to file if missing."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has docstring
    if content.strip().startswith('"""') or content.strip().startswith("'''"):
        print(f"✓ {filepath} already has docstring")
        return False
    
    separator = "=" * len(title)
    docstring = SERVICE_TEMPLATE.format(
        title=title,
        separator=separator,
        description=description,
        business_rules=business_rules or "Business rules enforced at service layer",
        dependencies=dependencies or "See __init__ method for dependencies"
    )
    
    # Insert after imports or at beginning
    lines = content.split('\n')
    insert_pos = 0
    
    # Find last import
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_pos = i + 1
    
    # Insert blank line and docstring
    lines.insert(insert_pos, docstring)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Added docstring to {filepath}")
    return True

def document_services():
    """Document all service files."""
    services_dir = Path(BACKEND_DIR) / "Services"
    
    service_docs = {
        "AnalyticsService.py": {
            "title": "Analytics Service - Business Intelligence",
            "description": "Provides analytics and reporting for business metrics.",
            "dependencies": "- ReportRepository\n    - MetricsCalculator"
        },
        "CurrencyConversionService.py": {
            "title": "Currency Conversion Service",
            "description": "Handles multi-currency support and exchange rates.",
            "dependencies": "- ExchangeRateProvider\n    - CurrencyRepository"
        },
        "LeaveManagementService.py": {
            "title": "Leave Management Service - PTO and Sick Leave",
            "description": "Manages employee time off requests and approvals.",
            "dependencies": "- EmployeeRepository\n    - LeaveRepository"
        },
        "PayrollService.py": {
            "title": "Payroll Service - Employee Compensation",
            "description": "Processes payroll, calculates wages, taxes, and deductions.",
            "dependencies": "- EmployeeRepository\n    - PayrollRepository"
        },
        "SchedulingService.py": {
            "title": "Scheduling Service - Employee Shifts",
            "description": "Manages employee scheduling and shift assignments.",
            "dependencies": "- EmployeeRepository\n    - ScheduleRepository"
        },
        "SellerService.py": {
            "title": "Seller Service - Marketplace Management",
            "description": "Manages seller accounts, products, and payouts.",
            "dependencies": "- SellerRepository\n    - ProductRepository"
        },
        "ShippingCarrierService.py": {
            "title": "Shipping Carrier Service - Carrier Integration",
            "description": "Integrates with shipping carriers for rates and tracking.",
            "dependencies": "- CarrierAPI\n    - ShipmentRepository"
        },
        "SimpleInventoryService.py": {
            "title": "Simple Inventory Service - Basic Stock Management",
            "description": "Simplified inventory operations for testing and development.",
            "dependencies": "- ProductRepository"
        },
        "TimeTrackingService.py": {
            "title": "Time Tracking Service - Employee Hours",
            "description": "Tracks employee clock in/out and hours worked.",
            "dependencies": "- EmployeeRepository\n    - HoursWorkedRepository"
        },
    }
    
    for filename, docs in service_docs.items():
        filepath = services_dir / filename
        if filepath.exists():
            add_module_docstring(
                filepath,
                docs["title"],
                docs["description"],
                dependencies=docs["dependencies"]
            )

def document_routers():
    """Document all router files."""
    routers_dir = Path(BACKEND_DIR) / "routers"
    
    router_docs = {
        "cart.py": "Cart API - Shopping cart operations",
        "catalog.py": "Catalog API - Product browsing and search",
        "checkout.py": "Checkout API - Order creation and payment",
        "orders.py": "Orders API - Order management and history",
        "payments.py": "Payments API - Payment processing",
        "products.py": "Products API - Product CRUD operations",
        "seller.py": "Seller API - Seller portal operations",
        "employee.py": "Employee API - Employee operations",
        "analytics.py": "Analytics API - Reports and metrics",
        "admin.py": "Admin API - Administrative operations",
    }
    
    for filename, title in router_docs.items():
        filepath = routers_dir / filename
        if filepath.exists():
            add_module_docstring(
                filepath,
                title,
                f"FastAPI router providing REST endpoints for {title.split(' - ')[1]}.",
                business_rules="See individual endpoint docstrings for business rules",
                dependencies="- Depends on corresponding service layer\n    - Uses FastAPI dependency injection"
            )

def document_utilities():
    """Document remaining utility files."""
    utils_dir = Path(BACKEND_DIR) / "Utilities"
    
    util_docs = {
        "csrf_protection.py": {
            "title": "CSRF Protection - Cross-Site Request Forgery Prevention",
            "description": "Implements CSRF token generation and validation for state-changing operations.",
        },
        "email.py": {
            "title": "Email Service - SMTP and Template Rendering",
            "description": "Handles email sending with template rendering and SMTP configuration.",
        },
        "input_sanitization.py": {
            "title": "Input Sanitization - XSS and SQL Injection Prevention",
            "description": "Sanitizes user input to prevent injection attacks and XSS.",
        },
    }
    
    for filename, docs in util_docs.items():
        filepath = utils_dir / filename
        if filepath.exists():
            add_module_docstring(
                filepath,
                docs["title"],
                docs["description"]
            )

def main():
    """Run documentation for all categories."""
    print("=" * 70)
    print("BACKEND DOCUMENTATION AUTOMATION")
    print("=" * 70)
    print()
    
    print("Documenting Services...")
    document_services()
    print()
    
    print("Documenting Routers...")
    document_routers()
    print()
    
    print("Documenting Utilities...")
    document_utilities()
    print()
    
    print("=" * 70)
    print("DOCUMENTATION COMPLETE!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Review generated docstrings for accuracy")
    print("2. Add method-level docstrings manually where needed")
    print("3. Update DOCUMENTATION_STATUS.md with progress")
    print()
    print("For detailed documentation of individual methods:")
    print("- Use Google-style docstrings (Args, Returns, Raises, Example)")
    print("- Explain business logic and WHY, not just WHAT")
    print("- Include usage examples for complex methods")

if __name__ == "__main__":
    main()
