"""
Product Search Agent - Main FastAPI Application

This is the main entry point for the Product Search Agent API.
It provides endpoints for managing search requests, viewing products,
and receiving real-time notifications.

Usage:
    uvicorn app.main:app --reload
    
API Documentation:
    http://localhost:8000/docs (Swagger UI)
    http://localhost:8000/redoc (ReDoc)
"""
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from app.api.routes import websocket
from app.core.scheduler import SearchScheduler
from app.config import settings


# Create global scheduler instance
scheduler = SearchScheduler()

from app.api.routes import scheduler as scheduler_routes





# Create FastAPI application instance
app = FastAPI(
    title="Product Search Agent API",
    description="""
    API for automated product search across multiple platforms.
    
    ## Features
    
    * **Search Requests**: Create and manage automated product searches
    * **Products**: View scraped products and matches
    * **Real-time Notifications**: Get notified when matches are found
    * **Multi-platform**: Search across Craigslist, Facebook Marketplace, and eBay
    
    ## Platforms Supported
    
    * Craigslist
    * Facebook Marketplace
    * eBay
    """,
    version="1.0.0",
    contact={
        "name": "Product Search Agent",
        "url": "https://github.com/yourusername/product-search-agent",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    redirect_slashes=False,  # Disable automatic trailing slash redirects to prevent CORS issues
)
# Include scheduler routes
app.include_router(scheduler_routes.router)

# Configure CORS (Cross-Origin Resource Sharing)
# This allows the frontend to communicate with the API
import os

# Build CORS origins list
origins = [
    settings.frontend_url,
    "http://localhost:5173",  # Local development
    "http://localhost:3000",  # Alternative local port
]

# Add Render-specific origins if deployed on Render
if os.getenv("RENDER"):
    # Add the actual frontend URL from environment
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        origins.append(frontend_url)
    
    # Add common Render frontend URLs
    origins.extend([
        "https://product-search-agent-ff7s.onrender.com",
    ])

# Add any additional origins from settings
if isinstance(settings.cors_origins, list):
    origins.extend(settings.cors_origins)

# Add CORS_ORIGINS from environment if set
cors_origins_env = os.getenv("CORS_ORIGINS")
if cors_origins_env:
    env_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
    origins.extend(env_origins)

# Remove duplicates while preserving order
origins = list(dict.fromkeys(origins))

# Log CORS origins for debugging
import logging
logger = logging.getLogger(__name__)
logger.info(f"CORS Origins configured: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Include router
app.include_router(
    websocket.router,
    tags=["websocket"]
)

from app.api.routes import digest

app.include_router(digest.router)
# ============================================================================
# Root Endpoints
# ============================================================================

@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint - API information and welcome message.
    
    Returns basic information about the API and links to documentation.
    
    Returns:
        dict: API information including name, version, and documentation links
    """
    return {
        "name": "Product Search Agent API",
        "version": "1.0.0",
        "description": "Automated product search across multiple platforms",
        "status": "running",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "health": "/api/health",
            "search_requests": "/api/search-requests",
            "products": "/api/products"
        }
    }


@app.get("/api/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    
    Used to verify that the API is running and responsive.
    Useful for monitoring, load balancers, and container orchestration.
    
    Returns:
        dict: Health status information including timestamp
    """
    return {
        "status": "healthy",
        "message": "Product Search Agent API is running",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# ============================================================================
# Application Lifecycle Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.
    
    This function is called when the FastAPI application starts.
    Use it to initialize resources, connect to databases, start background tasks, etc.
    """
    logger.info("\n" + "=" * 70)
    logger.info("🚀 Product Search Agent API Starting Up")
    logger.info("=" * 70)
    logger.info(f"📅 Started at: {datetime.utcnow().isoformat()}")
    logger.info(f"🌐 API Version: 1.0.0")
    logger.info(f"📚 API Documentation: http://localhost:8000/docs")
    logger.info(f"📖 Alternative Docs: http://localhost:8000/redoc")
    logger.info(f"💚 Health Check: http://localhost:8000/api/health")
    logger.info("🚀 Product Search Agent API starting up...")
    logger.info("📚 API Documentation: http://localhost:8000/docs")
    logger.info("=" * 70 + "\n")

  
    logger.info("\n" + "=" * 70)
    logger.info("🚀 Product Search Agent API Starting Up")
    logger.info("=" * 70)
    
    # Start the scheduler
    try:
        scheduler.start()
        logger.info("✅ Scheduler started successfully")
        
        # Log next run time
        next_run = scheduler.get_next_run_time()
        if next_run:
            logger.info(f"📅 Next search scheduled for: {next_run}")
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {str(e)}")
    
    logger.info("=" * 70 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown.
    
    This function is called when the FastAPI application shuts down.
    Use it to clean up resources, close database connections, stop background tasks, etc.
    """
    logger.info("\n" + "=" * 70)
    logger.info("👋 Product Search Agent API Shutting Down")
    logger.info("=" * 70)
    logger.info(f"📅 Stopped at: {datetime.utcnow().isoformat()}")
    logger.info("🧹 Cleaning up resources...")
    logger.info("=" * 70 + "\n")

    logger.info("\n" + "=" * 70)
    logger.info("🛑 Product Search Agent API Shutting Down")
    logger.info("=" * 70)
    
    # Shutdown the scheduler
    try:
        scheduler.shutdown()
        logger.info("✅ Scheduler shut down successfully")
    except Exception as e:
        logger.error(f"❌ Error shutting down scheduler: {str(e)}")
    
    logger.info("=" * 70 + "\n")


# ============================================================================
# Router Registration
# ============================================================================

# Import routers
from app.api.routes import search_requests, products, email_preferences

# Include routers in the application
app.include_router(search_requests.router)
app.include_router(products.router)
app.include_router(email_preferences.router)


# ============================================================================
# Error Handlers (Optional - for custom error responses)
# ============================================================================

# You can add custom error handlers here if needed
# Example:
# @app.exception_handler(404)
# async def not_found_handler(request, exc):
#     return JSONResponse(
#         status_code=404,
#         content={"message": "Resource not found"}
#     )


if __name__ == "__main__":
    # This allows running the app directly with: python -m app.main
    # However, it's recommended to use uvicorn command instead
    import uvicorn
    import os
    
    # Render provides PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

# Made with Bob
