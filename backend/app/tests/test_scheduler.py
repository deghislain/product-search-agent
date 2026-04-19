"""
Tests for Scheduler Service
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to Python path so we can import 'app' module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from app.core.scheduler import SearchScheduler


@pytest.fixture
def scheduler():
    """Create a scheduler instance for testing."""
    return SearchScheduler()

def test_scheduler_initialization(scheduler):
    """Test that scheduler initializes correctly."""
    assert scheduler is not None
    assert scheduler.is_running() == False

@pytest.mark.asyncio
async def test_scheduler_start(scheduler):
    """Test starting the scheduler."""
    # Start scheduler in async context
    scheduler.start()
    
    # Give it a moment to start
    await asyncio.sleep(0.1)
    
    assert scheduler.is_running() == True
    
    # Shutdown
    scheduler.shutdown()
    assert scheduler.is_running() == False

@pytest.mark.asyncio
async def test_scheduler_shutdown(scheduler):
    """Test shutting down the scheduler."""
    scheduler.start()
    # Give it a moment to start
    await asyncio.sleep(0.1)
    assert scheduler.is_running() == True
    
    scheduler.shutdown()
    assert scheduler.is_running() == False

@pytest.mark.asyncio
async def test_get_next_run_time(scheduler):
    """Test getting next run time."""
    # Before starting
    assert scheduler.get_next_run_time() is None
    
    # After starting
    scheduler.start()
    await asyncio.sleep(0.1)
    next_run = scheduler.get_next_run_time()
    assert next_run is not None
    
    scheduler.shutdown()

@pytest.mark.asyncio
async def test_get_job_info(scheduler):
    """Test getting job information."""
    # Before starting
    info = scheduler.get_job_info()
    assert info['status'] == 'stopped'
    
    # After starting
    scheduler.start()
    await asyncio.sleep(0.1)
    info = scheduler.get_job_info()
    assert info['status'] == 'running'
    assert info['job_id'] == 'search_job'
    
    scheduler.shutdown()

@pytest.mark.asyncio
async def test_run_all_searches(scheduler):
    """Test the search execution method."""
    with patch('app.core.scheduler.SessionLocal') as mock_session:
        with patch('app.core.scheduler.SearchOrchestrator') as mock_orchestrator:
            # Mock database session
            mock_db = Mock()
            mock_session.return_value = mock_db
            
            # Mock search requests
            mock_search = Mock()
            mock_search.id = 1
            mock_search.product_name = "Test Product"
            mock_search.location = "Test City"
            mock_db.query.return_value.filter.return_value.all.return_value = [mock_search]
            
            # Mock orchestrator
            mock_exec = Mock()
            mock_exec.status = 'completed'
            mock_exec.products_found = 5
            mock_exec.matches_found = 2
            mock_orchestrator.return_value.execute_search = AsyncMock(return_value=mock_exec)
            
            # Run the search
            await scheduler._run_all_searches()
            
            # Verify database was queried
            mock_db.query.assert_called_once()
            
            # Verify orchestrator was called
            mock_orchestrator.return_value.execute_search.assert_called_once()


@pytest.mark.asyncio
async def test_scheduler_start_already_running(scheduler):
    """Test starting scheduler when it's already running."""
    scheduler.start()
    await asyncio.sleep(0.1)
    
    # Try to start again - should log warning and return
    scheduler.start()
    
    assert scheduler.is_running() == True
    scheduler.shutdown()


@pytest.mark.asyncio
async def test_scheduler_start_with_exception(scheduler):
    """Test scheduler start handles exceptions."""
    # Mock add_job to raise an exception
    with patch.object(scheduler.scheduler, 'add_job', side_effect=Exception("Test error")):
        with pytest.raises(Exception, match="Test error"):
            scheduler.start()
    
    # Scheduler should not be running
    assert scheduler.is_running() == False


def test_scheduler_shutdown_not_running(scheduler):
    """Test shutting down scheduler when it's not running."""
    # Try to shutdown without starting - should log warning and return
    scheduler.shutdown()
    assert scheduler.is_running() == False


@pytest.mark.asyncio
async def test_scheduler_shutdown_with_exception(scheduler):
    """Test scheduler shutdown handles exceptions."""
    scheduler.start()
    await asyncio.sleep(0.1)
    
    # Mock shutdown to raise an exception
    with patch.object(scheduler.scheduler, 'shutdown', side_effect=Exception("Shutdown error")):
        with pytest.raises(Exception, match="Shutdown error"):
            scheduler.shutdown()


@pytest.mark.asyncio
async def test_run_all_searches_no_active_searches(scheduler):
    """Test _run_all_searches when there are no active searches."""
    with patch('app.core.scheduler.SessionLocal') as mock_session:
        # Mock database session
        mock_db = Mock()
        mock_session.return_value = mock_db
        
        # Mock empty search results
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        # Run the search - should return early
        await scheduler._run_all_searches()
        
        # Verify database was queried
        mock_db.query.assert_called_once()
        # Verify close was called
        mock_db.close.assert_called_once()


@pytest.mark.asyncio
async def test_run_all_searches_with_failed_execution(scheduler):
    """Test _run_all_searches when a search execution fails."""
    with patch('app.core.scheduler.SessionLocal') as mock_session:
        with patch('app.core.scheduler.SearchOrchestrator') as mock_orchestrator:
            # Mock database session
            mock_db = Mock()
            mock_session.return_value = mock_db
            
            # Mock search requests
            mock_search = Mock()
            mock_search.id = 1
            mock_search.product_name = "Test Product"
            mock_search.location = "Test City"
            mock_db.query.return_value.filter.return_value.all.return_value = [mock_search]
            
            # Mock orchestrator with failed execution
            mock_exec = Mock()
            mock_exec.status = 'failed'
            mock_exec.error_message = "Search failed"
            mock_orchestrator.return_value.execute_search = AsyncMock(return_value=mock_exec)
            
            # Run the search
            await scheduler._run_all_searches()
            
            # Verify orchestrator was called
            mock_orchestrator.return_value.execute_search.assert_called_once()


@pytest.mark.asyncio
async def test_run_all_searches_with_exception_in_search(scheduler):
    """Test _run_all_searches when an individual search raises an exception."""
    with patch('app.core.scheduler.SessionLocal') as mock_session:
        with patch('app.core.scheduler.SearchOrchestrator') as mock_orchestrator:
            # Mock database session
            mock_db = Mock()
            mock_session.return_value = mock_db
            
            # Mock two search requests
            mock_search1 = Mock()
            mock_search1.id = 1
            mock_search1.product_name = "Test Product 1"
            mock_search1.location = "Test City"
            
            mock_search2 = Mock()
            mock_search2.id = 2
            mock_search2.product_name = "Test Product 2"
            mock_search2.location = "Test City"
            
            mock_db.query.return_value.filter.return_value.all.return_value = [mock_search1, mock_search2]
            
            # Mock orchestrator - first call raises exception, second succeeds
            mock_exec = Mock()
            mock_exec.status = 'completed'
            mock_exec.products_found = 3
            mock_exec.matches_found = 1
            
            mock_orchestrator.return_value.execute_search = AsyncMock(
                side_effect=[Exception("Search error"), mock_exec]
            )
            
            # Run the search - should continue after exception
            await scheduler._run_all_searches()
            
            # Verify orchestrator was called twice
            assert mock_orchestrator.return_value.execute_search.call_count == 2


@pytest.mark.asyncio
async def test_run_all_searches_with_critical_exception(scheduler):
    """Test _run_all_searches when a critical exception occurs."""
    with patch('app.core.scheduler.SessionLocal') as mock_session:
        # Mock database session
        mock_db = Mock()
        mock_session.return_value = mock_db
        
        # Mock query to raise an exception
        mock_db.query.side_effect = Exception("Database error")
        
        # Run the search - should handle exception gracefully
        await scheduler._run_all_searches()
        
        # Verify close was called in finally block
        mock_db.close.assert_called_once()


@pytest.mark.asyncio
async def test_get_next_run_time_with_exception(scheduler):
    """Test get_next_run_time when an exception occurs."""
    scheduler.start()
    await asyncio.sleep(0.1)
    
    # Mock get_job to raise an exception
    with patch.object(scheduler.scheduler, 'get_job', side_effect=Exception("Job error")):
        result = scheduler.get_next_run_time()
        assert result is None
    
    scheduler.shutdown()


@pytest.mark.asyncio
async def test_get_job_info_no_job_found(scheduler):
    """Test get_job_info when job is not found."""
    scheduler.start()
    await asyncio.sleep(0.1)
    
    # Mock get_job to return None
    with patch.object(scheduler.scheduler, 'get_job', return_value=None):
        info = scheduler.get_job_info()
        assert info['status'] == 'running'
        assert info['message'] == 'No job found'
    
    scheduler.shutdown()


@pytest.mark.asyncio
async def test_get_job_info_with_exception(scheduler):
    """Test get_job_info when an exception occurs."""
    scheduler.start()
    await asyncio.sleep(0.1)
    
    # Mock get_job to raise an exception
    with patch.object(scheduler.scheduler, 'get_job', side_effect=Exception("Job info error")):
        info = scheduler.get_job_info()
        assert info['status'] == 'error'
        assert 'Job info error' in info['message']
    
    scheduler.shutdown()


@pytest.mark.asyncio
async def test_get_next_run_time_no_job(scheduler):
    """Test get_next_run_time when job is None."""
    scheduler.start()
    await asyncio.sleep(0.1)
    
    # Mock get_job to return None
    with patch.object(scheduler.scheduler, 'get_job', return_value=None):
        result = scheduler.get_next_run_time()
        assert result is None
    
    scheduler.shutdown()


def test_scheduler_start_no_event_loop():
    """Test scheduler start when there's no running event loop (non-async context)."""
    # Create scheduler in non-async context
    scheduler = SearchScheduler()
    
    # This should work but skip the immediate search execution
    # because there's no event loop
    with patch.object(scheduler.scheduler, 'start'):
        with patch.object(scheduler.scheduler, 'add_job'):
            scheduler.start()
            # The RuntimeError exception should be caught and logged
            assert scheduler.is_running() == True



# ============================================================================
# Daily Digest Tests
# ============================================================================

@pytest.mark.asyncio
async def test_send_daily_digest_success(scheduler):
    """Test _send_daily_digest with successful email sending."""
    with patch('app.core.scheduler.SessionLocal') as mock_session:
        # Mock database session
        mock_db = Mock()
        mock_session.return_value = mock_db
        
        # Mock digest data
        mock_digest_data = {
            'user1@example.com': [
                {'title': 'Product 1', 'price': 100, 'platform': 'craigslist'},
                {'title': 'Product 2', 'price': 200, 'platform': 'ebay'}
            ],
            'user2@example.com': [
                {'title': 'Product 3', 'price': 300, 'platform': 'facebook'}
            ]
        }
        
        # Mock email service methods
        scheduler.email_service.prepare_daily_digest_data = AsyncMock(return_value=mock_digest_data)
        scheduler.email_service.send_daily_digest = AsyncMock()
        
        # Run the digest
        await scheduler._send_daily_digest()
        
        # Verify prepare_daily_digest_data was called
        scheduler.email_service.prepare_daily_digest_data.assert_called_once_with(mock_db)
        
        # Verify send_daily_digest was called for each email
        assert scheduler.email_service.send_daily_digest.call_count == 2
        
        # Verify database session was closed
        mock_db.close.assert_called_once()


@pytest.mark.asyncio
async def test_send_daily_digest_no_data(scheduler):
    """Test _send_daily_digest when no digest data is available."""
    with patch('app.core.scheduler.SessionLocal') as mock_session:
        # Mock database session
        mock_db = Mock()
        mock_session.return_value = mock_db
        
        # Mock empty digest data
        scheduler.email_service.prepare_daily_digest_data = AsyncMock(return_value={})
        scheduler.email_service.send_daily_digest = AsyncMock()
        
        # Run the digest
        await scheduler._send_daily_digest()
        
        # Verify prepare_daily_digest_data was called
        scheduler.email_service.prepare_daily_digest_data.assert_called_once_with(mock_db)
        
        # Verify send_daily_digest was NOT called
        scheduler.email_service.send_daily_digest.assert_not_called()
        
        # Verify database session was closed
        mock_db.close.assert_called_once()


@pytest.mark.asyncio
async def test_send_daily_digest_partial_failure(scheduler):
    """Test _send_daily_digest when some emails fail to send."""
    with patch('app.core.scheduler.SessionLocal') as mock_session:
        # Mock database session
        mock_db = Mock()
        mock_session.return_value = mock_db
        
        # Mock digest data
        mock_digest_data = {
            'user1@example.com': [{'title': 'Product 1', 'price': 100}],
            'user2@example.com': [{'title': 'Product 2', 'price': 200}],
            'user3@example.com': [{'title': 'Product 3', 'price': 300}]
        }
        
        # Mock email service - second email fails
        scheduler.email_service.prepare_daily_digest_data = AsyncMock(return_value=mock_digest_data)
        scheduler.email_service.send_daily_digest = AsyncMock(
            side_effect=[None, Exception("SMTP error"), None]
        )
        
        # Run the digest - should not raise exception
        await scheduler._send_daily_digest()
        
        # Verify send_daily_digest was called 3 times
        assert scheduler.email_service.send_daily_digest.call_count == 3
        
        # Verify database session was closed
        mock_db.close.assert_called_once()


@pytest.mark.asyncio
async def test_send_daily_digest_prepare_data_exception(scheduler):
    """Test _send_daily_digest when prepare_daily_digest_data raises exception."""
    with patch('app.core.scheduler.SessionLocal') as mock_session:
        # Mock database session
        mock_db = Mock()
        mock_session.return_value = mock_db
        
        # Mock email service to raise exception
        scheduler.email_service.prepare_daily_digest_data = AsyncMock(
            side_effect=Exception("Database query error")
        )
        
        # Run the digest - should raise exception
        with pytest.raises(Exception, match="Database query error"):
            await scheduler._send_daily_digest()
        
        # Verify database session was closed in finally block
        mock_db.close.assert_called_once()


@pytest.mark.asyncio
async def test_send_daily_digest_all_emails_fail(scheduler):
    """Test _send_daily_digest when all emails fail to send."""
    with patch('app.core.scheduler.SessionLocal') as mock_session:
        # Mock database session
        mock_db = Mock()
        mock_session.return_value = mock_db
        
        # Mock digest data
        mock_digest_data = {
            'user1@example.com': [{'title': 'Product 1', 'price': 100}],
            'user2@example.com': [{'title': 'Product 2', 'price': 200}]
        }
        
        # Mock email service - all emails fail
        scheduler.email_service.prepare_daily_digest_data = AsyncMock(return_value=mock_digest_data)
        scheduler.email_service.send_daily_digest = AsyncMock(
            side_effect=Exception("SMTP connection failed")
        )
        
        # Run the digest - should not raise exception (errors are caught)
        await scheduler._send_daily_digest()
        
        # Verify send_daily_digest was called for each email
        assert scheduler.email_service.send_daily_digest.call_count == 2
        
        # Verify database session was closed
        mock_db.close.assert_called_once()


@pytest.mark.asyncio
async def test_send_daily_digest_database_session_cleanup(scheduler):
    """Test that database session is always closed even on exception."""
    with patch('app.core.scheduler.SessionLocal') as mock_session:
        # Mock database session
        mock_db = Mock()
        mock_session.return_value = mock_db
        
        # Mock email service to raise exception during prepare
        scheduler.email_service.prepare_daily_digest_data = AsyncMock(
            side_effect=Exception("Critical error")
        )
        
        # Run the digest - should raise exception
        with pytest.raises(Exception):
            await scheduler._send_daily_digest()
        
        # Verify database session was closed in finally block
        mock_db.close.assert_called_once()


@pytest.mark.asyncio
async def test_send_daily_digest_with_multiple_matches(scheduler):
    """Test _send_daily_digest with multiple matches per user."""
    with patch('app.core.scheduler.SessionLocal') as mock_session:
        # Mock database session
        mock_db = Mock()
        mock_session.return_value = mock_db
        
        # Mock digest data with many matches
        mock_digest_data = {
            'user@example.com': [
                {'title': f'Product {i}', 'price': i * 100, 'platform': 'craigslist'}
                for i in range(1, 11)  # 10 matches
            ]
        }
        
        # Mock email service
        scheduler.email_service.prepare_daily_digest_data = AsyncMock(return_value=mock_digest_data)
        scheduler.email_service.send_daily_digest = AsyncMock()
        
        # Run the digest
        await scheduler._send_daily_digest()
        
        # Verify send_daily_digest was called with correct data
        scheduler.email_service.send_daily_digest.assert_called_once()
        call_args = scheduler.email_service.send_daily_digest.call_args
        assert call_args[1]['email'] == 'user@example.com'
        assert len(call_args[1]['matches']) == 10
        
        # Verify database session was closed
        mock_db.close.assert_called_once()



# ============================================================================
# Monitoring and Job Info Tests
# ============================================================================

@pytest.mark.asyncio
async def test_get_digest_job_info_scheduled(scheduler):
    """Test get_digest_job_info when job is scheduled."""
    scheduler.start()
    await asyncio.sleep(0.1)
    
    info = scheduler.get_digest_job_info()
    
    assert info['status'] == 'scheduled'
    assert info['job_id'] == 'daily_digest_job'
    assert info['job_name'] == 'Send Daily Digest Emails'
    assert info['next_run_time'] is not None
    assert 'trigger' in info
    
    scheduler.shutdown()


@pytest.mark.asyncio
async def test_get_digest_job_info_not_scheduled(scheduler):
    """Test get_digest_job_info when job is not scheduled."""
    # Don't start scheduler
    info = scheduler.get_digest_job_info()
    
    assert info['status'] == 'not_scheduled'
    assert info['message'] == 'Daily digest job is not scheduled'
    assert info['next_run_time'] is None


@pytest.mark.asyncio
async def test_get_digest_job_info_with_exception(scheduler):
    """Test get_digest_job_info when an exception occurs."""
    scheduler.start()
    await asyncio.sleep(0.1)
    
    # Mock get_job to raise exception
    with patch.object(scheduler.scheduler, 'get_job', side_effect=Exception("Job error")):
        info = scheduler.get_digest_job_info()
        assert info['status'] == 'error'
        assert 'Job error' in info['message']
    
    scheduler.shutdown()


@pytest.mark.asyncio
async def test_get_all_jobs_info(scheduler):
    """Test get_all_jobs_info returns information about all jobs."""
    scheduler.start()
    await asyncio.sleep(0.1)
    
    info = scheduler.get_all_jobs_info()
    
    assert info['scheduler_running'] == True
    assert info['total_jobs'] == 2  # search_job and daily_digest_job
    assert len(info['jobs']) == 2
    
    # Check that both jobs are present
    job_ids = [job['id'] for job in info['jobs']]
    assert 'search_job' in job_ids
    assert 'daily_digest_job' in job_ids
    
    scheduler.shutdown()


@pytest.mark.asyncio
async def test_get_all_jobs_info_not_running(scheduler):
    """Test get_all_jobs_info when scheduler is not running."""
    # Don't start scheduler
    info = scheduler.get_all_jobs_info()
    
    assert info['scheduler_running'] == False
    assert info['total_jobs'] == 0


@pytest.mark.asyncio
async def test_get_all_jobs_info_with_exception(scheduler):
    """Test get_all_jobs_info when an exception occurs."""
    scheduler.start()
    await asyncio.sleep(0.1)
    
    # Mock get_jobs to raise exception
    with patch.object(scheduler.scheduler, 'get_jobs', side_effect=Exception("Jobs error")):
        info = scheduler.get_all_jobs_info()
        assert info['scheduler_running'] == True
        assert 'error' in info
        assert 'Jobs error' in info['error']
    
    scheduler.shutdown()
