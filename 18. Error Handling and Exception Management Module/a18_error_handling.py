"""
Module 18: Error Handling and Exception Management
Author: Member A
Description: Comprehensive error handling and exception management system
Dependencies: logging, traceback

Features:
- Custom exception classes
- Error logging and tracking
- Graceful error recovery
- Error reporting
- Exception chaining
- Debug utilities
"""

import logging
import traceback
import sys
from typing import Dict, Optional, Callable
from datetime import datetime
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels"""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


class LayerXException(Exception):
    """Base exception for LayerX system"""
    
    def __init__(self, message: str, error_code: str = None, 
                 severity: ErrorSeverity = ErrorSeverity.ERROR):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'exception_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'severity': self.severity.name,
            'timestamp': self.timestamp.isoformat()
        }


class EncryptionError(LayerXException):
    """Encryption-related errors"""
    pass


class DecryptionError(LayerXException):
    """Decryption-related errors"""
    pass


class KeyManagementError(LayerXException):
    """Key management errors"""
    pass


class ImageProcessingError(LayerXException):
    """Image processing errors"""
    pass


class EmbeddingError(LayerXException):
    """Embedding-related errors"""
    pass


class ExtractionError(LayerXException):
    """Extraction-related errors"""
    pass


class CompressionError(LayerXException):
    """Compression-related errors"""
    pass


class NetworkError(LayerXException):
    """Network communication errors"""
    pass


class ValidationError(LayerXException):
    """Data validation errors"""
    pass


class SecurityError(LayerXException):
    """Security-related errors"""
    pass


class ErrorHandler:
    """Centralized error handling system"""
    
    def __init__(self, log_file: str = "layerx_errors.log"):
        """
        Initialize error handler
        
        Args:
            log_file: Path to log file
        """
        self.log_file = log_file
        self.error_history = []
        self.error_callbacks = []
        
        # Setup logging
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('LayerX')
    
    def handle_exception(self, exception: Exception, 
                        context: str = None) -> Dict:
        """
        Handle exception with logging and tracking
        
        Args:
            exception: Exception to handle
            context: Additional context information
            
        Returns:
            Dictionary with error information
        """
        # Get traceback
        tb = traceback.format_exc()
        
        # Create error record
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'exception_type': type(exception).__name__,
            'message': str(exception),
            'context': context,
            'traceback': tb
        }
        
        # Add to history
        self.error_history.append(error_record)
        
        # Log based on severity
        if isinstance(exception, LayerXException):
            error_record.update(exception.to_dict())
            
            if exception.severity == ErrorSeverity.CRITICAL:
                self.logger.critical(f"{exception.message}\n{tb}")
            elif exception.severity == ErrorSeverity.ERROR:
                self.logger.error(f"{exception.message}\n{tb}")
            elif exception.severity == ErrorSeverity.WARNING:
                self.logger.warning(f"{exception.message}\n{tb}")
            else:
                self.logger.info(f"{exception.message}\n{tb}")
        else:
            self.logger.error(f"{str(exception)}\n{tb}")
        
        # Call callbacks
        for callback in self.error_callbacks:
            try:
                callback(error_record)
            except Exception as e:
                self.logger.error(f"Error in callback: {str(e)}")
        
        return error_record
    
    def add_callback(self, callback: Callable):
        """Add error callback function"""
        self.error_callbacks.append(callback)
    
    def get_error_history(self) -> list:
        """Get error history"""
        return self.error_history
    
    def get_recent_errors(self, count: int = 10) -> list:
        """Get most recent errors"""
        return self.error_history[-count:]
    
    def clear_history(self):
        """Clear error history"""
        self.error_history.clear()
    
    def get_error_summary(self) -> Dict:
        """Get error summary statistics"""
        if not self.error_history:
            return {'total': 0}
        
        error_types = {}
        for error in self.error_history:
            et = error['exception_type']
            error_types[et] = error_types.get(et, 0) + 1
        
        return {
            'total': len(self.error_history),
            'by_type': error_types,
            'latest': self.error_history[-1] if self.error_history else None
        }
    
    def print_summary(self):
        """Print error summary"""
        summary = self.get_error_summary()
        
        print("="*70)
        print("ERROR SUMMARY")
        print("="*70)
        print(f"Total Errors: {summary['total']}")
        
        if summary['total'] > 0:
            print("\nErrors by Type:")
            for error_type, count in summary['by_type'].items():
                print(f"   {error_type}: {count}")
            
            if summary['latest']:
                print("\nLatest Error:")
                print(f"   Type: {summary['latest']['exception_type']}")
                print(f"   Message: {summary['latest']['message']}")
                print(f"   Time: {summary['latest']['timestamp']}")
        
        print("="*70)


def safe_execute(func: Callable, *args, error_handler: ErrorHandler = None,
                default_return = None, context: str = None, **kwargs):
    """
    Safely execute function with error handling
    
    Args:
        func: Function to execute
        *args: Function arguments
        error_handler: ErrorHandler instance
        default_return: Value to return on error
        context: Context description
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or default_return on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if error_handler:
            error_handler.handle_exception(e, context)
        else:
            print(f"Error in {func.__name__}: {str(e)}")
        return default_return


def retry_on_error(func: Callable, max_retries: int = 3, 
                  delay: float = 1.0, error_handler: ErrorHandler = None):
    """
    Retry function on error
    
    Args:
        func: Function to execute
        max_retries: Maximum retry attempts
        delay: Delay between retries
        error_handler: ErrorHandler instance
        
    Returns:
        Decorator function
    """
    def wrapper(*args, **kwargs):
        import time
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if error_handler:
                    error_handler.handle_exception(
                        e, 
                        f"Retry attempt {attempt+1}/{max_retries}"
                    )
                
                if attempt < max_retries - 1:
                    time.sleep(delay)
                else:
                    raise
    
    return wrapper


class ErrorRecovery:
    """Error recovery strategies"""
    
    @staticmethod
    def recover_from_file_error(filepath: str, backup_path: str = None) -> bool:
        """
        Attempt to recover from file operation error
        
        Args:
            filepath: Original file path
            backup_path: Backup file path
            
        Returns:
            True if recovered
        """
        import os
        import shutil
        
        try:
            if backup_path and os.path.exists(backup_path):
                shutil.copy2(backup_path, filepath)
                return True
        except Exception:
            pass
        
        return False
    
    @staticmethod
    def recover_from_network_error(retry_func: Callable, 
                                   max_retries: int = 3) -> any:
        """
        Attempt to recover from network error
        
        Args:
            retry_func: Function to retry
            max_retries: Maximum retries
            
        Returns:
            Function result or None
        """
        import time
        
        for attempt in range(max_retries):
            try:
                return retry_func()
            except NetworkError:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
        
        return None
    
    @staticmethod
    def recover_from_memory_error() -> bool:
        """
        Attempt to recover from memory error
        
        Returns:
            True if recovered
        """
        import gc
        
        try:
            gc.collect()
            return True
        except Exception:
            return False


def validate_input(data: any, validator: Callable, 
                  error_message: str = "Validation failed") -> any:
    """
    Validate input data
    
    Args:
        data: Data to validate
        validator: Validation function
        error_message: Error message
        
    Returns:
        Validated data
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        if not validator(data):
            raise ValidationError(error_message, error_code="VAL001")
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(
            f"{error_message}: {str(e)}",
            error_code="VAL002"
        )
    
    return data


def test_error_handling():
    """Test error handling module"""
    print("="*70)
    print("MODULE 18: ERROR HANDLING TEST")
    print("="*70)
    
    # Initialize error handler
    handler = ErrorHandler("test_errors.log")
    
    # Add callback
    def error_callback(error_record):
        print(f"   📢 Callback: {error_record['exception_type']}")
    
    handler.add_callback(error_callback)
    
    # Test custom exceptions
    print("\n1. Testing custom exceptions...")
    try:
        raise EncryptionError("Test encryption error", error_code="ENC001")
    except EncryptionError as e:
        handler.handle_exception(e, "Test context")
        print(f"   ✓ Handled {e.__class__.__name__}")
    
    # Test safe execution
    print("\n2. Testing safe execution...")
    def failing_function():
        raise ValueError("Test error")
    
    result = safe_execute(
        failing_function,
        error_handler=handler,
        default_return="Safe default",
        context="Safe execution test"
    )
    print(f"   ✓ Safe execution returned: {result}")
    
    # Test validation
    print("\n3. Testing validation...")
    try:
        validate_input(
            "test",
            lambda x: len(x) > 10,
            "String too short"
        )
    except ValidationError as e:
        handler.handle_exception(e, "Validation test")
        print(f"   ✓ Validation error caught")
    
    # Test error recovery
    print("\n4. Testing error recovery...")
    import gc
    gc.collect()
    recovered = ErrorRecovery.recover_from_memory_error()
    print(f"   ✓ Memory recovery: {recovered}")
    
    # Print summary
    print("\n5. Error summary:")
    handler.print_summary()
    
    # Cleanup - close logger handlers first
    import os
    for h in handler.logger.handlers[:]:
        h.close()
        handler.logger.removeHandler(h)
    
    if os.path.exists("test_errors.log"):
        try:
            os.remove("test_errors.log")
        except PermissionError:
            print("   ⚠️  Could not remove log file (still in use)")
    
    print("\n" + "="*70)
    print("✅ Error handling module test completed!")
    print("="*70)


if __name__ == "__main__":
    test_error_handling()
