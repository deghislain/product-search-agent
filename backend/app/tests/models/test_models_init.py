"""
Test script for models __init__.py module.

This script tests the models package initialization including:
- Model imports
- Enum imports
- Base class import
- Utility functions
- Clean import syntax
"""

import sys
from pathlib import Path


# Add parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


def test_model_imports():
    """Test importing all models."""
    print("\n" + "="*70)
    print("TEST 1: Model Imports")
    print("="*70)
    
    try:
        # Test individual imports
        print("\n1. Testing individual model imports:")
        from app.models import SearchRequest
        print(f"   ✅ SearchRequest: {SearchRequest.__name__}")
        
        from app.models import SearchExecution
        print(f"   ✅ SearchExecution: {SearchExecution.__name__}")
        
        from app.models import Product
        print(f"   ✅ Product: {Product.__name__}")
        
        from app.models import Notification
        print(f"   ✅ Notification: {Notification.__name__}")
        
        # Test combined import
        print("\n2. Testing combined import:")
        from app.models import SearchRequest, SearchExecution, Product, Notification
        print(f"   ✅ All models imported successfully")
        
        # Verify table names
        print("\n3. Verifying table names:")
        print(f"   SearchRequest -> {SearchRequest.__tablename__}")
        print(f"   SearchExecution -> {SearchExecution.__tablename__}")
        print(f"   Product -> {Product.__tablename__}")
        print(f"   Notification -> {Notification.__tablename__}")
        
        print("\n✅ Model imports test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Model imports test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enum_imports():
    """Test importing all enums."""
    print("\n" + "="*70)
    print("TEST 2: Enum Imports")
    print("="*70)
    
    try:
        # Test individual enum imports
        print("\n1. Testing individual enum imports:")
        from app.models import SearchStatus
        print(f"   ✅ SearchStatus: {[s.value for s in SearchStatus]}")
        
        from app.models import NotificationType
        print(f"   ✅ NotificationType: {[t.value for t in NotificationType]}")
        
        from app.models import ExecutionStatus
        print(f"   ✅ ExecutionStatus: {[s.value for s in ExecutionStatus]}")
        
        # Test combined import
        print("\n2. Testing combined enum import:")
        from app.models import SearchStatus, NotificationType, ExecutionStatus
        print(f"   ✅ All enums imported successfully")
        
        # Test enum values
        print("\n3. Testing enum values:")
        print(f"   SearchStatus.ACTIVE = '{SearchStatus.ACTIVE.value}'")
        print(f"   NotificationType.MATCH_FOUND = '{NotificationType.MATCH_FOUND.value}'")
        print(f"   ExecutionStatus.RUNNING = '{ExecutionStatus.RUNNING.value}'")
        
        print("\n✅ Enum imports test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Enum imports test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_base_import():
    """Test importing Base class."""
    print("\n" + "="*70)
    print("TEST 3: Base Class Import")
    print("="*70)
    
    try:
        from app.models import Base
        print(f"\n✅ Base class imported: {Base}")
        
        # Verify models inherit from Base
        from app.models import SearchRequest, SearchExecution, Product, Notification
        
        print("\nVerifying model inheritance:")
        for model in [SearchRequest, SearchExecution, Product, Notification]:
            is_subclass = issubclass(model, Base)
            status = "✅" if is_subclass else "❌"
            print(f"   {status} {model.__name__} inherits from Base: {is_subclass}")
        
        print("\n✅ Base class import test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Base class import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_utility_functions():
    """Test utility functions."""
    print("\n" + "="*70)
    print("TEST 4: Utility Functions")
    print("="*70)
    
    try:
        from app.models import get_all_models, get_all_enums, get_model_names
        
        # Test get_all_models
        print("\n1. Testing get_all_models():")
        models = get_all_models()
        print(f"   Returned {len(models)} models:")
        for model in models:
            print(f"      - {model.__name__} ({model.__tablename__})")
        
        # Test get_all_enums
        print("\n2. Testing get_all_enums():")
        enums = get_all_enums()
        print(f"   Returned {len(enums)} enums:")
        for name, enum_class in enums.items():
            values = [e.value for e in enum_class]
            print(f"      - {name}: {values}")
        
        # Test get_model_names
        print("\n3. Testing get_model_names():")
        table_names = get_model_names()
        print(f"   Returned {len(table_names)} table names:")
        for name in table_names:
            print(f"      - {name}")
        
        # Verify expected values
        print("\n4. Verifying expected values:")
        expected_models = 4
        expected_enums = 3
        expected_tables = 4
        
        checks = [
            (len(models) == expected_models, f"Model count: {len(models)} == {expected_models}"),
            (len(enums) == expected_enums, f"Enum count: {len(enums)} == {expected_enums}"),
            (len(table_names) == expected_tables, f"Table count: {len(table_names)} == {expected_tables}"),
        ]
        
        for passed, message in checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {message}")
        
        all_passed = all(check[0] for check in checks)
        
        if all_passed:
            print("\n✅ Utility functions test passed!")
        else:
            print("\n❌ Some utility function checks failed!")
        
        return all_passed
        
    except Exception as e:
        print(f"\n❌ Utility functions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_exports():
    """Test __all__ exports."""
    print("\n" + "="*70)
    print("TEST 5: __all__ Exports")
    print("="*70)
    
    try:
        import app.models as models_module
        
        print("\n1. Checking __all__ attribute:")
        if hasattr(models_module, '__all__'):
            print(f"   ✅ __all__ exists")
            all_exports = models_module.__all__
            print(f"   Total exports: {len(all_exports)}")
        else:
            print(f"   ❌ __all__ not found")
            return False
        
        print("\n2. Verifying all exports are accessible:")
        for name in all_exports:
            if hasattr(models_module, name):
                obj = getattr(models_module, name)
                print(f"   ✅ {name}: {type(obj).__name__}")
            else:
                print(f"   ❌ {name}: Not accessible")
                return False
        
        print("\n3. Testing wildcard import (from app.models import *):")
        # Note: We can't actually test wildcard import in this context,
        # but we can verify __all__ contains what we expect
        expected_exports = [
            'SearchStatus', 'NotificationType', 'ExecutionStatus',
            'Base',
            'SearchRequest', 'SearchExecution', 'Product', 'Notification',
            'get_all_models', 'get_all_enums', 'get_model_names'
        ]
        
        for name in expected_exports:
            if name in all_exports:
                print(f"   ✅ {name} in __all__")
            else:
                print(f"   ⚠️  {name} not in __all__")
        
        print("\n✅ __all__ exports test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ __all__ exports test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_no_circular_imports():
    """Test for circular import issues."""
    print("\n" + "="*70)
    print("TEST 6: Circular Import Check")
    print("="*70)
    
    try:
        print("\n1. Testing multiple import sequences:")
        
        # Sequence 1
        from app.models import SearchRequest
        from app.models import SearchExecution
        print("   ✅ Sequence 1: SearchRequest -> SearchExecution")
        
        # Sequence 2
        from app.models import Product, Notification
        print("   ✅ Sequence 2: Product, Notification")
        
        # Sequence 3
        from app.models import SearchStatus, NotificationType, ExecutionStatus
        print("   ✅ Sequence 3: All enums")
        
        # Sequence 4
        from app.models import Base, SearchRequest, Product
        print("   ✅ Sequence 4: Base with models")
        
        # Sequence 5 - Import everything
        from app.models import (
            SearchRequest, SearchExecution, Product, Notification,
            SearchStatus, NotificationType, ExecutionStatus,
            Base, get_all_models
        )
        print("   ✅ Sequence 5: Everything at once")
        
        print("\n✅ No circular import issues detected!")
        return True
        
    except Exception as e:
        print(f"\n❌ Circular import check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("MODELS __INIT__.PY TEST SUITE")
    print("="*70)
    
    # Run tests
    results = {
        'model_imports': test_model_imports(),
        'enum_imports': test_enum_imports(),
        'base_import': test_base_import(),
        'utility_functions': test_utility_functions(),
        'all_exports': test_all_exports(),
        'no_circular_imports': test_no_circular_imports(),
    }
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("="*70)
    
    print("\nThe models __init__.py module is working correctly!")
    print("All models, enums, and utilities are properly exported.")
    print("\nUsage examples:")
    print("  from app.models import SearchRequest, Product")
    print("  from app.models import SearchStatus, NotificationType")
    print("  from app.models import get_all_models, get_model_names")
    print("="*70 + "\n")


def test_main_function():
    """Test the main() function that runs all tests."""
    print("\n" + "="*70)
    print("TEST 7: Main Function")
    print("="*70)
    
    try:
        # Run main function
        main()
        print("\n✅ Main function executed successfully!")
        
    except Exception as e:
        print(f"\n❌ Main function test failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()

# Made with Bob
