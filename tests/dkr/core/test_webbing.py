from keri.db import subing
from keri.vdr import credentialing
from mockito import mock, verify, when

from dkr.core import didding
from dkr.core.webbing import load_endpoints


def test_setup():
    app = mock()
    hby = mock()
    hby.name = 'test_hab'
    hby.base = 'test_base'

    rgy = mock(credentialing.Regery)
    rgy.reger = mock(credentialing.Reger)
    rgy.reger.issus = mock(subing.CesrDupSuber)
    rgy.reger.schms = mock(subing.CesrDupSuber)
    when(rgy.reger.issus).get(keys='test_aid').thenReturn([])
    when(rgy.reger.schms).get(keys=didding.DES_ALIASES_SCHEMA).thenReturn([])

    load_endpoints(app, hby, rgy)

    verify(app, times=1).add_route('/{aid}/did.json', any)
    verify(app, times=1).add_route('/{aid}/keri.cesr', any)
