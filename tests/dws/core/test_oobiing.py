from hio.help import Mict
from keri import kering
from keri.app.habbing import Hab, Habery
from keri.core.eventing import Kever
from keri.db.basing import Baser, EndpointRecord
from keri.db.koming import Komer
from mockito import mock, unstub, when

from dws.core import oobiing


def test_generate_oobi_by_alias_works():
    hby = mock(Habery)
    hab = mock(Hab)
    hab.kever = mock(Kever)
    hab.kever.wits = ['WITNESS1']
    hab.pre = 'TESTPRE'

    # Test HTTP URL
    when(hby).habByName(name='test_alias').thenReturn(hab)
    when(hab).fetchUrls(eid='WITNESS1', scheme='http').thenReturn(Mict([('http', 'http://127.0.0.1:6645/')]))

    oobi = oobiing.generate_oobi(hby=hby, alias='test_alias')
    assert oobi == 'http://127.0.0.1:6645/oobi/TESTPRE/witness'

    # Test HTTPS URL
    unstub()

    hby = mock(Habery)
    hab = mock(Hab)
    hab.kever = mock(Kever)
    hab.kever.wits = ['WITNESS1']
    hab.pre = 'TESTPRE'

    when(hby).habByName(name='test_alias').thenReturn(hab)
    when(hab).fetchUrls(eid='WITNESS1', scheme='http').thenReturn(Mict([('http', 'http://127.0.0.1:6645/')]))

    oobi = oobiing.generate_oobi(hby=hby, alias='test_alias')
    assert oobi == 'http://127.0.0.1:6645/oobi/TESTPRE/witness'


def test_generate_oobi_no_urls_raises_configuration_error():
    hby = mock(Habery)
    hab = mock(Hab)
    hab.kever = mock(Kever)
    hab.kever.wits = ['WITNESS1']
    hab.pre = 'TESTPRE'

    when(hby).habByName(name='test_alias').thenReturn(hab)

    # have to mock both protocols since both are checked
    when(hab).fetchUrls(eid='WITNESS1', scheme='http').thenReturn(None)
    when(hab).fetchUrls(eid='WITNESS1', scheme='https').thenReturn(None)

    oobi = oobiing.generate_oobi(hby=hby, alias='test_alias')
    assert oobi is None


def test_generate_oobi_controller_url_works():
    hby = mock(Habery)
    hab = mock(Hab)
    hab.pre = 'TESTPRE'

    # Test HTTP URL
    when(hby).habByName(name='test_alias').thenReturn(hab)
    when(hab).fetchUrls(eid='TESTPRE', scheme='http').thenReturn(Mict([('http', 'http://127.0.0.1:6645/')]))

    oobi = oobiing.generate_oobi(hby=hby, alias='test_alias', role=kering.Roles.controller)
    assert oobi == 'http://127.0.0.1:6645/oobi/TESTPRE/controller'

    # Test HTTPS URL
    unstub()
    hby = mock(Habery)
    hab = mock(Hab)
    hab.pre = 'TESTPRE'

    when(hby).habByName(name='test_alias').thenReturn(hab)
    when(hab).fetchUrls(eid='TESTPRE', scheme='http').thenReturn(None)
    when(hab).fetchUrls(eid='TESTPRE', scheme='https').thenReturn(Mict([('https', 'https://127.0.0.1:6645/')]))

    oobi = oobiing.generate_oobi(hby=hby, alias='test_alias', role=kering.Roles.controller)
    assert oobi == 'https://127.0.0.1:6645/oobi/TESTPRE/controller'


def test_generate_oobi_controller_no_urls():
    hby = mock(Habery)
    hab = mock(Hab)
    hab.pre = 'TESTPRE'

    when(hby).habByName(name='test_alias').thenReturn(hab)
    when(hab).fetchUrls(eid='TESTPRE', scheme='http').thenReturn(None)
    when(hab).fetchUrls(eid='TESTPRE', scheme='https').thenReturn(None)

    oobi = oobiing.generate_oobi(hby=hby, alias='test_alias', role=kering.Roles.controller)
    assert oobi is None


def test_generate_oobi_mailbox_url_works():
    hby = mock(Habery)
    hab = mock(Hab)
    hab.db = mock(Baser)
    hab.db.ends = mock(Komer)
    aid_alias = 'test_alias'
    aid_pre = 'TESTPRE'
    hab.pre = aid_pre
    mbx_pre = 'MBXPRE'
    end = EndpointRecord(name='mailbox-for-test', allowed=True, enabled=True)

    # Test HTTP URL
    when(hby).habByName(name=aid_alias).thenReturn(hab)
    when(hab.db.ends).getItemIter(keys=(aid_pre, kering.Roles.mailbox)).thenReturn([((aid_pre, 'mailbox', mbx_pre), end)])
    when(hab).fetchUrls(eid=mbx_pre, scheme='http').thenReturn(Mict([('http', 'http://127.0.0.1:6645/')]))

    oobi = oobiing.generate_oobi(hby=hby, alias=aid_alias, role=kering.Roles.mailbox)
    assert oobi == f'http://127.0.0.1:6645/oobi/{aid_pre}/mailbox/{mbx_pre}'

    # Test HTTPS URL
    unstub()

    hby = mock(Habery)
    hab = mock(Hab)
    hab.db = mock(Baser)
    hab.db.ends = mock(Komer)
    hab.pre = aid_pre

    when(hby).habByName(name=aid_alias).thenReturn(hab)
    when(hab.db.ends).getItemIter(keys=(aid_pre, kering.Roles.mailbox)).thenReturn([((aid_pre, 'mailbox', mbx_pre), end)])
    when(hab).fetchUrls(eid=mbx_pre, scheme='http').thenReturn(None)
    when(hab).fetchUrls(eid=mbx_pre, scheme='https').thenReturn(Mict([('https', 'https://127.0.0.1:6645/')]))

    oobi = oobiing.generate_oobi(hby=hby, alias=aid_alias, role=kering.Roles.mailbox)
    assert oobi == f'https://127.0.0.1:6645/oobi/{aid_pre}/mailbox/{mbx_pre}'


def test_generate_oobi_mailbox_disabled_endpoint_continues():
    hby = mock(Habery)
    hab = mock(Hab)
    hab.db = mock(Baser)
    hab.db.ends = mock(Komer)
    aid_alias = 'test_alias'
    aid_pre = 'TESTPRE'
    hab.pre = aid_pre
    mbx1_pre = 'MBX1PRE'
    mbx2_pre = 'MBX2PRE'
    end1 = EndpointRecord(name='mailbox1', allowed=True, enabled=False)
    end2 = EndpointRecord(name='mailbox2', allowed=True, enabled=True)

    # Test HTTP URL
    when(hby).habByName(name=aid_alias).thenReturn(hab)
    when(hab.db.ends).getItemIter(keys=(aid_pre, kering.Roles.mailbox)).thenReturn(
        [
            ((aid_pre, 'mailbox', mbx1_pre), end1),
            ((aid_pre, 'mailbox', mbx2_pre), end2),
        ]
    )
    when(hab).fetchUrls(eid=mbx2_pre, scheme='http').thenReturn(Mict([('http', 'http://127.0.0.1:6645/')]))
    oobi = oobiing.generate_oobi(hby=hby, alias=aid_alias, role=kering.Roles.mailbox)
    assert oobi == f'http://127.0.0.1:6645/oobi/{aid_pre}/mailbox/{mbx2_pre}'


def test_generate_oobi_mailbox_no_urls_returns_none():
    hby = mock(Habery)
    hab = mock(Hab)
    hab.db = mock(Baser)
    hab.db.ends = mock(Komer)
    aid_alias = 'test_alias'
    aid_pre = 'TESTPRE'
    hab.pre = aid_pre
    mbx_pre = 'MBXPRE'
    end = EndpointRecord(name='mailbox-for-test', allowed=True, enabled=True)

    when(hby).habByName(name=aid_alias).thenReturn(hab)
    when(hab.db.ends).getItemIter(keys=(aid_pre, kering.Roles.mailbox)).thenReturn([((aid_pre, 'mailbox', mbx_pre), end)])
    when(hab).fetchUrls(eid=mbx_pre, scheme='http').thenReturn(None)
    when(hab).fetchUrls(eid=mbx_pre, scheme='https').thenReturn(None)

    oobi = oobiing.generate_oobi(hby=hby, alias=aid_alias, role=kering.Roles.mailbox)
    assert oobi is None
