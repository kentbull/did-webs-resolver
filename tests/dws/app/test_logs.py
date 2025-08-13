import pytest

from dws import log_format_str, log_name


def test_truncated_formatter():
    """Test the TruncatedFormatter class."""
    import logging

    from dws.app.logs import TruncatedFormatter

    # Create an instance of TruncatedFormatter
    formatter = TruncatedFormatter(log_format_str)
    log_message = 'This is a test message.'
    formatted = formatter.format(
        logging.LogRecord(
            name='test_logger',
            level=logging.DEBUG,
            func='test_truncated_formatter',
            pathname='tests/dws/app/test_logs.py',
            lineno=42,
            msg=log_message,
            args=None,
            exc_info=None,
            sinfo=None,
        )
    )
    assert 'DEBUG' in formatted
    assert log_name in formatted
    assert 'test_logs' in formatted
    assert 'test_truncated' in formatted
    assert '42' in formatted
    assert log_message in formatted

    with pytest.raises(TypeError):
        formatter.format(
            logging.LogRecord(
                name='test_logger',
                level=logging.DEBUG,
                func='test_truncated_formatter',
                pathname='tests/dws/app/test_logs.py',
                lineno=42,
                msg='%s %s',
                args=('one',),  # invalid log message since expects two args and only one present
                exc_info=None,
                sinfo=None,
            )
        )
