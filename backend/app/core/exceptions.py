"""
Exception handling for the application
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from typing import Union

logger = logging.getLogger(__name__)

class AppException(Exception):
    """Base application exception"""
    
    def __init__(self, message: str, code: str = "APP_ERROR", details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

class DocumentProcessingError(AppException):
    """Document processing related errors"""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "DOCUMENT_PROCESSING_ERROR", details)

class FileValidationError(AppException):
    """File validation related errors"""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "FILE_VALIDATION_ERROR", details)

class SearchError(AppException):
    """Search related errors"""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "SEARCH_ERROR", details)

async def app_exception_handler(request: Request, exc: AppException):
    """Handle application exceptions"""
    logger.error(f"Application error: {exc.code} - {exc.message}", extra={"details": exc.details})
    
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": exc.message,
            "code": exc.code,
            "details": exc.details
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "code": f"HTTP_{exc.status_code}"
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "An unexpected error occurred",
            "code": "INTERNAL_SERVER_ERROR"
        }
    )

def setup_exception_handlers(app: FastAPI):
    """Setup exception handlers for the FastAPI app"""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
