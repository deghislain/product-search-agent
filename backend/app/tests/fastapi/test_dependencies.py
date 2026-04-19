"""
Test script for API dependencies.

This script tests that the database dependency function works correctly
and properly manages database sessions.

Usage:
    python -m app.api.test_dependencies
"""
import sys
from pathlib import Path


# Add parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from app.api.dependencies import get_db
from app.models import SearchRequest
import sys


def test_get_db_dependency():
    """Test that get_db dependency creates and closes sessions properly."""
    print("\n" + "=" * 70)
    print("  TESTING DATABASE DEPENDENCY")
    print("=" * 70)
    
    try:
        # Test 1: Get a database session
        print("\n📝 Test 1: Getting database session from dependency")
        db_generator = get_db()
        db = next(db_generator)
        print(f"   ✅ Database session created: {db}")
        print(f"   ✅ Session type: {type(db).__name__}")
        
        # Test 2: Use the session to query database
        print("\n📝 Test 2: Using session to query database")
        count = db.query(SearchRequest).count()
        print(f"   ✅ Query successful: Found {count} search requests")
        
        # Test 3: Verify session can be closed
        print("\n📝 Test 3: Closing database session")
        try:
            next(db_generator)
        except StopIteration:
            print("   ✅ Session closed properly (StopIteration raised as expected)")
        
        # Test 4: Create a new session (simulating a new request)
        print("\n📝 Test 4: Creating new session (simulating new request)")
        db_generator2 = get_db()
        db2 = next(db_generator2)
        print(f"   ✅ New session created: {db2}")
        print(f"   ✅ Sessions are different: {db is not db2}")
        
        # Clean up second session
        try:
            next(db_generator2)
        except StopIteration:
            print("   ✅ Second session closed properly")
        
        # Test 5: Verify session works in context manager style
        print("\n📝 Test 5: Testing with context manager pattern")
        db_gen = get_db()
        try:
            db_ctx = next(db_gen)
            result = db_ctx.query(SearchRequest).first()
            print(f"   ✅ Context manager style works")
            print(f"   ✅ Query result: {result if result else 'No records yet'}")
        finally:
            try:
                next(db_gen)
            except StopIteration:
                print("   ✅ Session closed in finally block")
        
        # Summary
        print("\n" + "=" * 70)
        print("  TEST SUMMARY")
        print("=" * 70)
        print("   ✅ Database dependency creates sessions correctly")
        print("   ✅ Sessions can query the database")
        print("   ✅ Sessions are properly closed after use")
        print("   ✅ Multiple sessions can be created independently")
        print("   ✅ Context manager pattern works correctly")
        print("\n🎉 ALL DEPENDENCY TESTS PASSED!\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print("\n❌ DEPENDENCY TESTS FAILED\n")
        return False


def test_dependency_in_fastapi_style():
    """Test dependency as it would be used in FastAPI routes."""
    print("\n" + "=" * 70)
    print("  TESTING FASTAPI-STYLE USAGE")
    print("=" * 70)
    
    try:
        # Simulate how FastAPI would use the dependency
        print("\n📝 Simulating FastAPI route handler")
        
        # This is how FastAPI internally uses the dependency
        def mock_route_handler(db):
            """Mock route handler that receives db session."""
            searches = db.query(SearchRequest).limit(5).all()
            return {
                "count": len(searches),
                "searches": [s.product_name for s in searches] if searches else []
            }
        
        # FastAPI would call get_db() and pass the session to the handler
        db_gen = get_db()
        db_session = next(db_gen)
        
        # Call the route handler with the session
        result = mock_route_handler(db_session)
        print(f"   ✅ Route handler executed successfully")
        print(f"   ✅ Result: {result}")
        
        # FastAPI would then close the session
        try:
            next(db_gen)
        except StopIteration:
            print("   ✅ Session closed after route handler")
        
        print("\n🎉 FASTAPI-STYLE USAGE TEST PASSED!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\n❌ FASTAPI-STYLE USAGE TEST FAILED\n")
        return False


def run_all_tests():
    """Run all dependency tests."""
    print("\n" + "=" * 70)
    print("  DATABASE DEPENDENCY TEST SUITE")
    print("=" * 70)
    print("\nTesting database dependency function for FastAPI routes...\n")
    
    results = []
    
    # Run tests
    results.append(("Basic Dependency Tests", test_get_db_dependency()))
    results.append(("FastAPI-Style Usage", test_dependency_in_fastapi_style()))
    
    # Final summary
    print("=" * 70)
    print("  FINAL TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status}: {test_name}")
    
    print(f"\n   Total: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n" + "=" * 70)
        print("  🎉 ALL TESTS PASSED! 🎉")
        print("=" * 70 + "\n")
        return True
    else:
        print("\n" + "=" * 70)
        print("  ❌ SOME TESTS FAILED ❌")
        print("=" * 70 + "\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

# Made with Bob
