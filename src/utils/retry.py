"""Retry and circuit breaker utilities for resilient API calls."""
import time
import functools
from typing import TypeVar, Callable, Any, Optional, Type, Tuple
from loguru import logger
from .errors import (
    PaperpileNotionError, 
    GoogleDriveError, 
    GeminiAPIError, 
    NotionAPIError
)

T = TypeVar('T')


class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection."""
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF_OPEN'
                logger.info(f"Circuit breaker entering HALF_OPEN state for {func.__name__}")
            else:
                raise PaperpileNotionError(
                    f"Circuit breaker is OPEN for {func.__name__}. "
                    f"Retry after {self.recovery_timeout - (time.time() - self.last_failure_time):.0f}s"
                )
        
        try:
            result = func(*args, **kwargs)
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
                logger.info(f"Circuit breaker reset to CLOSED for {func.__name__}")
            return result
        except Exception as e:
            self._record_failure()
            raise e
    
    def _record_failure(self):
        """Record a failure and potentially open the circuit."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(f"Circuit breaker OPENED after {self.failure_count} failures")


def exponential_backoff_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """Decorator for exponential backoff retry logic."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"{func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
                        raise
                    
                    # Calculate next delay
                    delay = min(delay * exponential_base, max_delay)
                    
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


def api_retry(service: str) -> Callable:
    """Specialized retry decorator for API calls."""
    exception_map = {
        'google_drive': (GoogleDriveError, ConnectionError, TimeoutError),
        'gemini': (GeminiAPIError, ConnectionError, TimeoutError),
        'notion': (NotionAPIError, ConnectionError, TimeoutError),
    }
    
    exceptions = exception_map.get(service, (Exception,))
    
    return exponential_backoff_retry(
        max_retries=3,
        initial_delay=1.0,
        exponential_base=2.0,
        max_delay=30.0,
        exceptions=exceptions
    )


class RateLimiter:
    """Rate limiter for API calls."""
    
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.last_call_time = 0
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limit."""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.min_interval:
            sleep_time = self.min_interval - time_since_last_call
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_call_time = time.time()
    
    def __enter__(self):
        """Context manager entry."""
        self.wait_if_needed()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass