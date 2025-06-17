"""
Configure PyTest

Use this module to configure pytest
https://docs.pytest.org/en/latest/pythonpath.html

"""

import pytest
from keri.help import helping


@pytest.fixture()
def mock_helping_now_utc(monkeypatch):
    """
    Replace nowUTC universally with fixed value for testing
    """

    def mock_now_utc():
        """
        Use predetermined value for now (current time)
        '2021-01-01T00:00:00.000000+00:00'
        """
        return helping.fromIso8601('2021-01-01T00:00:00.000000+00:00')

    monkeypatch.setattr(helping, 'nowUTC', mock_now_utc)
