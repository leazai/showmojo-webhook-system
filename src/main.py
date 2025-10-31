"""
ShowMojo Webhook System - Main FastAPI Application
"""

from fastapi import FastAPI, Request, Depends, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import os
import logging
from dotenv import load_dotenv

from .database import get_db, init_db
from .schemas import WebhookPayload, WebhookResponse
from .webhook_service import WebhookService
from .api_routes import router as api_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ShowMojo Webhook System",
    description="Real-time webhook listener and database system for ShowMojo listings, leads, and showings",
    version="1.0.0"
)

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ShowMojo Bearer Token for authentication
SHOWMOJO_BEARER_TOKEN = os.getenv("SHOWMOJO_BEARER_TOKEN", "")

# Include API router
app.include_router(api_router)


def verify_bearer_token(authorization: Optional[str] = Header(None)) -> bool:
    """
    Verify Bearer token from ShowMojo webhook
    
    Args:
        authorization: Authorization header value
        
    Returns:
        True if token is valid
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not SHOWMOJO_BEARER_TOKEN:
        logger.warning("SHOWMOJO_BEARER_TOKEN not configured, skipping authentication")
        return True
    
    if not authorization:
        logger.error("Missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )
    
    if not authorization.startswith("Bearer "):
        logger.error("Invalid Authorization header format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format"
        )
    
    token = authorization.replace("Bearer ", "")
    if token != SHOWMOJO_BEARER_TOKEN:
        logger.error("Invalid Bearer token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Bearer token"
        )
    
    return True


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting ShowMojo Webhook System...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "service": "ShowMojo Webhook System",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/webhook", response_model=WebhookResponse)
async def receive_webhook(
    request: Request,
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_bearer_token)
):
    """
    Receive and process ShowMojo webhook
    
    This endpoint receives POST requests from ShowMojo with lead and showing data.
    It validates the payload, stores it in the database, and returns a 200 OK response.
    
    Args:
        request: FastAPI request object
        db: Database session
        authorized: Bearer token verification result
        
    Returns:
        WebhookResponse with processing status
    """
    try:
        # Get raw payload
        payload = await request.json()
        logger.info(f"Received webhook with action: {payload.get('event', {}).get('action', 'unknown')}")
        
        # Process webhook
        result = WebhookService.process_webhook(payload, db)
        
        # Return success response
        return WebhookResponse(
            status=result["status"],
            message=result["message"],
            event_id=result.get("event_id")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
