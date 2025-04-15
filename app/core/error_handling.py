"""
Enhanced error handling utilities for TORONTO AI TEAM AGENT.

This module provides robust error handling and logging capabilities for critical integration points.
"""

import logging
import traceback
from enum import Enum
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union, cast

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("toronto_ai_team_agent.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("toronto_ai_team_agent")

# Type definitions
T = TypeVar('T')
R = TypeVar('R')


class ErrorSeverity(Enum):
    """Enum representing the severity of errors."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ErrorCategory(Enum):
    """Enum representing categories of errors."""
    CONFIGURATION = "CONFIGURATION"
    INTEGRATION = "INTEGRATION"
    MULTIMODAL = "MULTIMODAL"
    ORCHESTRATION = "ORCHESTRATION"
    CODE_GENERATION = "CODE_GENERATION"
    VECTOR_DB = "VECTOR_DB"
    AUTHENTICATION = "AUTHENTICATION"
    NETWORK = "NETWORK"
    UNKNOWN = "UNKNOWN"


class EnhancedError(Exception):
    """Enhanced error class with additional context information."""
    
    def __init__(
        self, 
        message: str, 
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        original_error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.category = category
        self.severity = severity
        self.original_error = original_error
        self.context = context or {}
        self.traceback = traceback.format_exc() if original_error else None
        
        # Construct the full error message
        full_message = f"[{severity.value}][{category.value}] {message}"
        if original_error:
            full_message += f" | Original error: {str(original_error)}"
        
        super().__init__(full_message)
        
        # Log the error
        self._log_error()
    
    def _log_error(self) -> None:
        """Log the error with appropriate severity level."""
        log_message = f"{self.message}"
        if self.context:
            log_message += f" | Context: {self.context}"
        
        if self.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, exc_info=self.original_error)
        elif self.severity == ErrorSeverity.HIGH:
            logger.error(log_message, exc_info=self.original_error)
        elif self.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message, exc_info=self.original_error)
        else:
            logger.info(log_message, exc_info=self.original_error)


def safe_execute(
    func: Callable[..., R],
    error_category: ErrorCategory,
    error_message: str,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    default_return: Optional[R] = None,
    raise_error: bool = False,
    context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> R:
    """
    Safely execute a function with enhanced error handling.
    
    Args:
        func: The function to execute
        error_category: Category of potential errors
        error_message: Message to use if an error occurs
        severity: Severity level of potential errors
        default_return: Value to return if an error occurs and raise_error is False
        raise_error: Whether to raise the enhanced error or return default_return
        context: Additional context information to include in error
        **kwargs: Arguments to pass to the function
        
    Returns:
        The result of the function or default_return if an error occurs
        
    Raises:
        EnhancedError: If an error occurs and raise_error is True
    """
    try:
        return func(**kwargs)
    except Exception as e:
        error_context = context or {}
        error_context.update({"function": func.__name__, "arguments": str(kwargs)})
        
        enhanced_error = EnhancedError(
            message=error_message,
            category=error_category,
            severity=severity,
            original_error=e,
            context=error_context
        )
        
        if raise_error:
            raise enhanced_error
        
        # If we're not raising, return the default
        return cast(R, default_return)


class ErrorHandler:
    """Context manager for enhanced error handling."""
    
    def __init__(
        self,
        error_category: ErrorCategory,
        error_message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        raise_error: bool = True,
        context: Optional[Dict[str, Any]] = None
    ):
        self.error_category = error_category
        self.error_message = error_message
        self.severity = severity
        self.raise_error = raise_error
        self.context = context or {}
    
    def __enter__(self) -> 'ErrorHandler':
        return self
    
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[traceback.TracebackType]
    ) -> bool:
        if exc_val is not None:
            enhanced_error = EnhancedError(
                message=self.error_message,
                category=self.error_category,
                severity=self.severity,
                original_error=exc_val if isinstance(exc_val, Exception) else None,
                context=self.context
            )
            
            if self.raise_error:
                raise enhanced_error from exc_val
            
            # Suppress the original exception
            return True
        
        return False


def configure_logging(log_file: str = "toronto_ai_team_agent.log", log_level: int = logging.INFO) -> None:
    """
    Configure logging for the application.
    
    Args:
        log_file: Path to the log file
        log_level: Logging level (e.g., logging.INFO, logging.DEBUG)
    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
