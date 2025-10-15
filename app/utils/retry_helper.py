# app/utils/retry_helper.py

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

# Configure logger for retries
logger = logging.getLogger(__name__)


def retry_on_exception(
    max_attempts: int = 3,
    wait_initial: int = 2,
    wait_max: int = 10,
    exceptions: tuple = (Exception,),
):
    """
    Decorator to retry a function call on exceptions.

    Args:
        max_attempts (int): Maximum retry attempts before failing.
        wait_initial (int): Initial wait time (in seconds) before retry.
        wait_max (int): Maximum wait time (in seconds) between retries.
        exceptions (tuple): Exception types that trigger retry.

    Usage:
        @retry_on_exception(max_attempts=5, wait_initial=1)
        def fetch_data():
            # your logic here
            pass
    """
    def decorator(func):
        return retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=wait_initial, max=wait_max),
            retry=retry_if_exception_type(exceptions),
            reraise=True,
            before_sleep=lambda retry_state: logger.warning(
                f"[RetryHelper] Retrying {func.__name__} (attempt {retry_state.attempt_number}/{max_attempts}) "
                f"due to {retry_state.outcome.exception()}"
            ),
        )(func)

    return decorator
