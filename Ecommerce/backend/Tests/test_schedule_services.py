"""
Tests for Schedule Services - Simple Verification

Quick tests to verify the refactored schedule services work correctly.
"""

import sys
import os
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

def test_schedule_filter_service_imports():
    """Test that ScheduleFilterService imports correctly."""
    from Services.ScheduleFilterService import ScheduleFilterService
    assert ScheduleFilterService is not None
    print("✅ ScheduleFilterService imports successfully")


def test_schedule_comparison_service_imports():
    """Test that ScheduleComparisonService imports correctly."""
    from Services.ScheduleComparisonService import ScheduleComparisonService
    assert ScheduleComparisonService is not None
    print("✅ ScheduleComparisonService imports successfully")


def test_simple_schedule_comparison_imports():
    """Test that SimpleScheduleComparison imports correctly."""
    from Services.SimpleScheduleComparison import SimpleScheduleComparison
    assert SimpleScheduleComparison is not None
    print("✅ SimpleScheduleComparison imports successfully")


def test_schedule_filter_service_has_correct_methods():
    """Test that ScheduleFilterService has the expected method."""
    from Services.ScheduleFilterService import ScheduleFilterService
    
    # Check that the new method exists
    assert hasattr(ScheduleFilterService, 'find_available_employees_on_date')
    
    # Check that old methods are removed
    assert not hasattr(ScheduleFilterService, 'get_employees_by_criteria')
    assert not hasattr(ScheduleFilterService, 'get_department_schedule')
    assert not hasattr(ScheduleFilterService, 'get_position_hierarchy_schedule')
    
    print("✅ ScheduleFilterService has correct methods")


def test_schedule_comparison_service_has_correct_methods():
    """Test that ScheduleComparisonService has the expected methods."""
    from Services.ScheduleComparisonService import ScheduleComparisonService
    
    # Check that the new methods exist
    assert hasattr(ScheduleComparisonService, 'find_employee_ids_by_criteria')
    assert hasattr(ScheduleComparisonService, 'get_employee_schedules_in_period')
    
    # Check that old methods are removed
    assert not hasattr(ScheduleComparisonService, 'get_overlapping_shifts_with_target')
    assert not hasattr(ScheduleComparisonService, 'get_team_schedule_matrix')
    assert not hasattr(ScheduleComparisonService, 'find_common_shifts')
    
    print("✅ ScheduleComparisonService has correct methods")


def test_simple_schedule_comparison_has_correct_methods():
    """Test that SimpleScheduleComparison has the expected methods."""
    from Services.SimpleScheduleComparison import SimpleScheduleComparison
    
    # Check that the method exists
    assert hasattr(SimpleScheduleComparison, 'find_all_by_position_and_location')
    
    # Check that old method is removed
    assert not hasattr(SimpleScheduleComparison, 'compare_with_target')
    
    print("✅ SimpleScheduleComparison has correct methods")


def test_simple_inventory_service_has_correct_methods():
    """Test that SimpleInventoryService has unused methods removed."""
    from Services.SimpleInventoryService import SimpleInventoryService
    
    # Check that removed methods are gone
    assert not hasattr(SimpleInventoryService, 'get_low_stock_products')
    assert not hasattr(SimpleInventoryService, 'batch_reserve_stock')
    
    # Check that kept methods still exist
    assert hasattr(SimpleInventoryService, 'check_availability')
    assert hasattr(SimpleInventoryService, 'reserve_stock')
    assert hasattr(SimpleInventoryService, 'release_stock')
    assert hasattr(SimpleInventoryService, 'update_stock_level')
    assert hasattr(SimpleInventoryService, 'get_stock_level')
    assert hasattr(SimpleInventoryService, 'restock_product')
    
    print("✅ SimpleInventoryService has correct methods")


def test_method_signatures():
    """Test that methods have correct signatures."""
    from Services.ScheduleFilterService import ScheduleFilterService
    from Services.ScheduleComparisonService import ScheduleComparisonService
    from Services.SimpleScheduleComparison import SimpleScheduleComparison
    import inspect
    
    # Check ScheduleFilterService.find_available_employees_on_date
    sig = inspect.signature(ScheduleFilterService.find_available_employees_on_date)
    params = list(sig.parameters.keys())
    assert 'self' in params
    assert 'target_date' in params
    assert 'time_start' in params
    assert 'time_end' in params
    assert 'department' in params
    assert 'position' in params
    assert 'location' in params
    assert 'availability_type' in params
    
    # Check ScheduleComparisonService.find_employee_ids_by_criteria
    sig = inspect.signature(ScheduleComparisonService.find_employee_ids_by_criteria)
    params = list(sig.parameters.keys())
    assert 'self' in params
    assert 'department' in params
    assert 'position' in params
    assert 'location' in params
    assert 'exclude_employee_ids' in params
    
    # Check ScheduleComparisonService.get_employee_schedules_in_period
    sig = inspect.signature(ScheduleComparisonService.get_employee_schedules_in_period)
    params = list(sig.parameters.keys())
    assert 'self' in params
    assert 'employee_ids' in params
    assert 'start_date' in params
    assert 'end_date' in params
    
    # Check SimpleScheduleComparison.find_all_by_position_and_location
    sig = inspect.signature(SimpleScheduleComparison.find_all_by_position_and_location)
    params = list(sig.parameters.keys())
    assert 'self' in params
    assert 'position' in params
    assert 'location' in params
    assert 'start_date' in params
    assert 'end_date' in params
    
    print("✅ All method signatures are correct")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("SCHEDULE SERVICES REFACTORING VERIFICATION")
    print("="*60 + "\n")
    
    try:
        test_schedule_filter_service_imports()
        test_schedule_comparison_service_imports()
        test_simple_schedule_comparison_imports()
        test_schedule_filter_service_has_correct_methods()
        test_schedule_comparison_service_has_correct_methods()
        test_simple_schedule_comparison_has_correct_methods()
        test_simple_inventory_service_has_correct_methods()
        test_method_signatures()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")
        print("Summary:")
        print("  - All services import successfully")
        print("  - All unused methods removed")
        print("  - All new methods implemented")
        print("  - All method signatures correct")
        print()
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
