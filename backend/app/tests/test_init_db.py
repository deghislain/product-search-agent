"""
Test script for database initialization module.

This script tests the init_db module functionality including:
- Database initialization
- Database verification
- Database statistics
- All command-line actions
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.models.init_db import init_db, verify_db, get_db_stats, drop_db, reset_db, main


def test_init_db_success():
    """Test successful database initialization."""
    result = init_db(verbose=True)
    assert result is True
    print("\n✅ Database initialization with verbose=True passed")
    
    result = init_db(verbose=False)
    assert result is True
    print("✅ Database initialization with verbose=False passed")


def test_init_db_exception():
    """Test init_db with exception."""
    with patch('app.models.init_db.Base.metadata.create_all', side_effect=Exception("DB Error")):
        result = init_db(verbose=True)
        assert result is False
        print("\n✅ init_db exception handling (verbose=True) tested (lines 75-80)")
    
    with patch('app.models.init_db.Base.metadata.create_all', side_effect=Exception("DB Error")):
        result = init_db(verbose=False)
        assert result is False
        print("✅ init_db exception handling (verbose=False) tested")


def test_verify_db_success():
    """Test successful database verification."""
    result = verify_db(verbose=True)
    assert result is True
    print("\n✅ Database verification with verbose=True passed")
    
    result = verify_db(verbose=False)
    assert result is True
    print("✅ Database verification with verbose=False passed")


def test_verify_db_connection_failure():
    """Test verify_db when connection fails."""
    with patch('app.models.init_db.check_db_connection', return_value=False):
        result = verify_db(verbose=True)
        assert result is False
        print("\n✅ verify_db connection failure (verbose=True) tested (lines 215-217)")
    
    with patch('app.models.init_db.check_db_connection', return_value=False):
        result = verify_db(verbose=False)
        assert result is False
        print("✅ verify_db connection failure (verbose=False) tested")


def test_verify_db_missing_tables():
    """Test verify_db when tables are missing."""
    mock_inspector = Mock()
    mock_inspector.get_table_names = Mock(return_value=['search_requests'])  # Missing other tables
    
    with patch('app.models.init_db.inspect', return_value=mock_inspector):
        with patch('app.models.init_db.check_db_connection', return_value=True):
            result = verify_db(verbose=True)
            assert result is False
            print("\n✅ verify_db missing tables (verbose=True) tested (lines 230-233)")
    
    with patch('app.models.init_db.inspect', return_value=mock_inspector):
        with patch('app.models.init_db.check_db_connection', return_value=True):
            result = verify_db(verbose=False)
            assert result is False
            print("✅ verify_db missing tables (verbose=False) tested")


def test_verify_db_exception():
    """Test verify_db with exception."""
    with patch('app.models.init_db.check_db_connection', side_effect=Exception("Connection error")):
        result = verify_db(verbose=True)
        assert result is False
        print("\n✅ verify_db exception handling (verbose=True) tested (lines 259-264)")
    
    with patch('app.models.init_db.check_db_connection', side_effect=Exception("Connection error")):
        result = verify_db(verbose=False)
        assert result is False
        print("✅ verify_db exception handling (verbose=False) tested")


def test_get_db_stats_success():
    """Test successful database statistics retrieval."""
    stats = get_db_stats(verbose=True)
    assert isinstance(stats, dict)
    assert 'search_requests' in stats
    assert 'search_executions' in stats
    assert 'products' in stats
    assert 'notifications' in stats
    print("\n✅ get_db_stats with verbose=True passed")
    
    stats = get_db_stats(verbose=False)
    assert isinstance(stats, dict)
    print("✅ get_db_stats with verbose=False passed")


def test_get_db_stats_exception():
    """Test get_db_stats with exception."""
    with patch('app.models.init_db.SessionLocal', side_effect=Exception("DB Error")):
        stats = get_db_stats(verbose=True)
        assert stats == {}
        print("\n✅ get_db_stats exception handling (verbose=True) tested (lines 310-313)")
    
    with patch('app.models.init_db.SessionLocal', side_effect=Exception("DB Error")):
        stats = get_db_stats(verbose=False)
        assert stats == {}
        print("✅ get_db_stats exception handling (verbose=False) tested")


def test_drop_db_with_confirmation_yes():
    """Test drop_db with confirmation (user says yes)."""
    with patch('builtins.input', return_value='yes'):
        result = drop_db(verbose=True, confirm=True)
        assert result is True
        print("\n✅ drop_db with confirmation='yes' tested (lines 110-115)")


def test_drop_db_with_confirmation_no():
    """Test drop_db with confirmation (user says no)."""
    with patch('builtins.input', return_value='no'):
        result = drop_db(verbose=True, confirm=True)
        assert result is False
        print("\n✅ drop_db with confirmation='no' tested (lines 110-115)")


def test_drop_db_without_confirmation():
    """Test drop_db without confirmation."""
    result = drop_db(verbose=True, confirm=False)
    assert result is True
    print("\n✅ drop_db without confirmation tested")


def test_drop_db_exception():
    """Test drop_db with exception."""
    with patch('app.models.init_db.Base.metadata.drop_all', side_effect=Exception("Drop error")):
        result = drop_db(verbose=True, confirm=False)
        assert result is False
        print("\n✅ drop_db exception handling (verbose=True) tested (lines 141-146)")
    
    with patch('app.models.init_db.Base.metadata.drop_all', side_effect=Exception("Drop error")):
        result = drop_db(verbose=False, confirm=False)
        assert result is False
        print("✅ drop_db exception handling (verbose=False) tested")


def test_reset_db_success():
    """Test successful database reset."""
    result = reset_db(verbose=True, confirm=False)
    assert result is True
    print("\n✅ reset_db success tested")


def test_reset_db_drop_fails():
    """Test reset_db when drop fails."""
    with patch('app.models.init_db.drop_db', return_value=False):
        result = reset_db(verbose=True, confirm=False)
        assert result is False
        print("\n✅ reset_db drop failure tested (line 177)")


def test_reset_db_init_fails():
    """Test reset_db when init fails."""
    with patch('app.models.init_db.drop_db', return_value=True):
        with patch('app.models.init_db.init_db', return_value=False):
            result = reset_db(verbose=True, confirm=False)
            assert result is False
            print("\n✅ reset_db init failure tested (line 181)")


def test_main_init_action():
    """Test main() with init action."""
    test_args = ['prog', 'init']
    with patch('sys.argv', test_args):
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_called_once_with(0)
    print("\n✅ main() init action tested (line 345)")


def test_main_drop_action():
    """Test main() with drop action."""
    test_args = ['prog', 'drop', '--no-confirm']
    with patch('sys.argv', test_args):
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_called_once_with(0)
    print("\n✅ main() drop action tested (line 347)")


def test_main_reset_action():
    """Test main() with reset action."""
    test_args = ['prog', 'reset', '--no-confirm']
    with patch('sys.argv', test_args):
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_called_once_with(0)
    print("\n✅ main() reset action tested (line 349)")


def test_main_verify_action():
    """Test main() with verify action."""
    test_args = ['prog', 'verify']
    with patch('sys.argv', test_args):
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_called_once_with(0)
    print("\n✅ main() verify action tested (line 351)")


def test_main_stats_action():
    """Test main() with stats action."""
    test_args = ['prog', 'stats']
    with patch('sys.argv', test_args):
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_called_once_with(0)
    print("\n✅ main() stats action tested (lines 353-354)")


def test_main_with_quiet_flag():
    """Test main() with --quiet flag."""
    test_args = ['prog', 'init', '--quiet']
    with patch('sys.argv', test_args):
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_called_once_with(0)
    print("\n✅ main() with --quiet flag tested (line 341)")


def test_main_with_no_confirm_flag():
    """Test main() with --no-confirm flag."""
    test_args = ['prog', 'drop', '--no-confirm']
    with patch('sys.argv', test_args):
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_called_once_with(0)
    print("\n✅ main() with --no-confirm flag tested (line 342)")


def test_main_failure():
    """Test main() when action fails."""
    test_args = ['prog', 'init']
    with patch('sys.argv', test_args):
        with patch('app.models.init_db.init_db', return_value=False):
            with patch('sys.exit') as mock_exit:
                main()
                mock_exit.assert_called_once_with(1)
    print("\n✅ main() failure exit code tested (line 359)")


def test_main_stats_empty():
    """Test main() with stats action returning empty dict."""
    test_args = ['prog', 'stats']
    with patch('sys.argv', test_args):
        with patch('app.models.init_db.get_db_stats', return_value={}):
            with patch('sys.exit') as mock_exit:
                main()
                mock_exit.assert_called_once_with(1)
    print("\n✅ main() stats with empty result tested")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])

# Made with Bob
