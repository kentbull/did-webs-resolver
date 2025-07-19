from mockito import mock, verify

from dkr.core.webbing import load_endpoints


def test_setup():
    app = mock()
    hby = mock()
    hby.name = 'test_hab'
    hby.base = 'test_base'

    load_endpoints(app, hby)

    verify(app, times=1).add_route('/{aid}/did.json', any)
    verify(app, times=1).add_route('/{aid}/keri.cesr', any)
