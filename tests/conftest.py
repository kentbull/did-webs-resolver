"""
Configure PyTest

Use this module to configure pytest
https://docs.pytest.org/en/latest/pythonpath.html

"""


import pytest
from keri.help import helping

WitnessUrls = {
    'wan:tcp': 'tcp://127.0.0.1:5632/',
    'wan:http': 'http://127.0.0.1:5642/',
    'wes:tcp': 'tcp://127.0.0.1:5634/',
    'wes:http': 'http://127.0.0.1:5644/',
    'wil:tcp': 'tcp://127.0.0.1:5633/',
    'wil:http': 'http://127.0.0.1:5643/',
}


@pytest.fixture()
def mockHelpingNowUTC(monkeypatch):
    """
    Replace nowUTC universally with fixed value for testing
    """

    def mockNowUTC():
        """
        Use predetermined value for now (current time)
        '2021-01-01T00:00:00.000000+00:00'
        """
        return helping.fromIso8601('2021-01-01T00:00:00.000000+00:00')

    monkeypatch.setattr(helping, 'nowUTC', mockNowUTC)
