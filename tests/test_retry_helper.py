import pytest
from app.utils.retry_helper import retry_on_exception

class CustomError(Exception):
    pass


def test_retry_success_after_failures():
    """Should retry twice and succeed on the third attempt."""
    call_count = {"count": 0}

    @retry_on_exception(max_attempts=3, wait_initial=0.1)
    def flaky_function():
        call_count["count"] += 1
        if call_count["count"] < 3:
            raise CustomError("Temporary error")
        return "Success"

    result = flaky_function()
    assert result == "Success"
    assert call_count["count"] == 3  # retried twice


def test_retry_fails_after_max_attempts():
    """Should fail after all retry attempts are exhausted."""
    call_count = {"count": 0}

    @retry_on_exception(max_attempts=3, wait_initial=0.1)
    def always_fail():
        call_count["count"] += 1
        raise CustomError("Still failing")

    with pytest.raises(CustomError):
        always_fail()

    assert call_count["count"] == 3  # retried 3 times total


def test_retry_ignores_other_exceptions():
    """Should not retry for non-specified exceptions."""
    call_count = {"count": 0}

    @retry_on_exception(max_attempts=5, exceptions=(CustomError,))
    def raise_value_error():
        call_count["count"] += 1
        raise ValueError("Wrong exception type")

    with pytest.raises(ValueError):
        raise_value_error()

    assert call_count["count"] == 1  # should not retry
