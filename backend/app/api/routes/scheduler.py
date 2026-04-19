"""
Scheduler API Routes

Endpoints for checking and managing the scheduler.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.main import scheduler

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])

@router.get("/status")
async def get_scheduler_status() -> Dict[str, Any]:
    """
    Get the current status of the scheduler.
    
    Returns:
        dict: Scheduler status including next run time
        
    Example Response:
        ```json
        {
            "status": "running",
            "is_running": true,
            "next_run": "2024-01-15T14:30:00",
            "job_info": {
                "job_id": "search_job",
                "name": "Run All Product Searches",
                "trigger": "interval[0:02:00:00]"
            }
        }
        ```
    """
    try:
        is_running = scheduler.is_running()
        next_run = scheduler.get_next_run_time()
        job_info = scheduler.get_job_info()
        
        return {
            "status": "running" if is_running else "stopped",
            "is_running": is_running,
            "next_run": next_run.isoformat() if next_run else None,
            "job_info": job_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting scheduler status: {str(e)}"
        )
        
@router.post("/trigger")
async def trigger_search_now() -> Dict[str, str]:
    """
    Manually trigger a search execution now.
    
    This runs all active searches immediately without waiting
    for the scheduled time.
    
    Returns:
        dict: Success message
        
    Example Response:
        ```json
        {
            "message": "Search execution triggered successfully"
        }
        ```
    """
    try:
        if not scheduler.is_running():
            raise HTTPException(
                status_code=400,
                detail="Scheduler is not running"
            )
        
        # Trigger the search job immediately
        await scheduler._run_all_searches()
        
        return {
            "message": "Search execution triggered successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error triggering search: {str(e)}"
        )


@router.get("/digest/status")
async def get_digest_job_status() -> Dict[str, Any]:
    """
    Get the status of the daily digest job.
    
    Returns:
        dict: Digest job status including next run time
        
    Example Response:
        ```json
        {
            "status": "scheduled",
            "job_id": "daily_digest_job",
            "job_name": "Send Daily Digest Emails",
            "next_run_time": "2024-01-16T09:00:00",
            "trigger": "cron[hour='9', minute='0']",
            "message": "Next digest will be sent at 2024-01-16 09:00:00"
        }
        ```
    """
    try:
        digest_info = scheduler.get_digest_job_info()
        return digest_info
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting digest job status: {str(e)}"
        )


@router.get("/jobs")
async def get_all_jobs() -> Dict[str, Any]:
    """
    Get information about all scheduled jobs.
    
    Returns:
        dict: Information about all jobs (search and digest)
        
    Example Response:
        ```json
        {
            "scheduler_running": true,
            "total_jobs": 2,
            "jobs": [
                {
                    "id": "search_job",
                    "name": "Run All Product Searches",
                    "next_run_time": "2024-01-15T14:30:00",
                    "trigger": "interval[0:02:00:00]"
                },
                {
                    "id": "daily_digest_job",
                    "name": "Send Daily Digest Emails",
                    "next_run_time": "2024-01-16T09:00:00",
                    "trigger": "cron[hour='9', minute='0']"
                }
            ]
        }
        ```
    """
    try:
        jobs_info = scheduler.get_all_jobs_info()
        return jobs_info
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting jobs information: {str(e)}"
        )


@router.get("/health")
async def scheduler_health_check() -> Dict[str, Any]:
    """
    Health check endpoint for the scheduler.
    
    Checks if the scheduler is running and all jobs are properly scheduled.
    
    Returns:
        dict: Health status of the scheduler
        
    Example Response:
        ```json
        {
            "status": "healthy",
            "scheduler_running": true,
            "jobs_scheduled": 2,
            "search_job": "scheduled",
            "digest_job": "scheduled",
            "message": "All systems operational"
        }
        ```
    """
    try:
        is_running = scheduler.is_running()
        jobs_info = scheduler.get_all_jobs_info()
        
        # Check if both jobs are scheduled
        search_job_scheduled = any(job['id'] == 'search_job' for job in jobs_info.get('jobs', []))
        digest_job_scheduled = any(job['id'] == 'daily_digest_job' for job in jobs_info.get('jobs', []))
        
        # Determine overall health
        if is_running and search_job_scheduled and digest_job_scheduled:
            status = "healthy"
            message = "All systems operational"
        elif is_running:
            status = "degraded"
            message = "Scheduler running but some jobs not scheduled"
        else:
            status = "unhealthy"
            message = "Scheduler not running"
        
        return {
            "status": status,
            "scheduler_running": is_running,
            "jobs_scheduled": jobs_info.get('total_jobs', 0),
            "search_job": "scheduled" if search_job_scheduled else "not_scheduled",
            "digest_job": "scheduled" if digest_job_scheduled else "not_scheduled",
            "message": message
        }
    except Exception as e:
        return {
            "status": "error",
            "scheduler_running": False,
            "message": f"Error checking health: {str(e)}"
        }