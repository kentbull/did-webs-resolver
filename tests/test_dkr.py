import logging

from dkr import log_name, ogler, set_log_level


def test_set_log_level():
    logger = ogler.getLogger(log_name)
    assert logger.level == logging.INFO  # Default log level
    set_log_level('debug', logger)
    assert logger.level == logging.DEBUG
