from unittest.mock import patch
from app.tasks.monitoring import monitor_dlq_depth

def test_monitor_dlq_depth_exception_path():
    with patch("app.tasks.monitoring.redis.from_url") as mock_from_url:
        with patch("app.tasks.monitoring.logger.error") as mock_logger_error:
            # Simulate an exception when trying to connect to redis
            mock_from_url.side_effect = Exception("Redis connection failed")

            # Call the function
            result = monitor_dlq_depth()

            # Check the results
            assert result is None
            mock_logger_error.assert_called_once_with("Failed to monitor DLQ: Redis connection failed")
