from mockito import mock, verify

from dkr.core.webbing import setup


def test_setup():
    app = mock()
    hby = mock()

    setup(app, hby)

    verify(app, times=1).add_route("/{aid}/did.json", any)
    verify(app, times=1).add_route("/{aid}/keri.cesr", any)
