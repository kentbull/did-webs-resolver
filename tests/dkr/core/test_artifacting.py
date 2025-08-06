import pytest
from keri import kering
from keri.app import habbing
from keri.app.habbing import Habery
from keri.core import eventing
from keri.db import basing, koming
from keri.vdr.credentialing import Regery
from mockito import mock, when

from dkr import DidWebsError
from dkr.core import artifacting


def test_make_keri_cesr_path_with_nonexistent_dir_creates_path():
    """
    Test that make_keri_cesr_path creates the necessary directories when the output directory does not exist.
    """
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        aid = 'test_aid'
        path = artifacting.make_keri_cesr_path(temp_dir, aid)
        assert os.path.exists(os.path.dirname(path))
        assert path == os.path.join(temp_dir, aid)  # Check the full path


def test_make_did_json_path_with_nonexistent_dir_creates_path():
    """
    Test that make_did_json_path creates the necessary directories when the output directory does not exist.
    """
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        aid = 'test_aid'
        path = artifacting.make_did_json_path(temp_dir, aid)
        assert os.path.exists(os.path.dirname(path))
        assert path == os.path.join(temp_dir, aid)  # Check the full path


def test_generate_artifacts_no_diddoc_raises_didwebs_error():
    """
    Test that generate_artifacts raises DidWebsError when the DID document generation fails.
    """

    hby = Habery(name='test_hab', base='test_base')
    rgy = Regery(hby=hby, name='test_regery')

    did = 'did:webs:example.com%3A1234:test_path:EJg2UL2kSzFV_Akd9ISAvgOUFDKcBxpDO3OZDIbSIjGe'

    with pytest.raises(DidWebsError):
        artifacting.generate_artifacts(hby, rgy, did, meta=True, output_dir='./tests/artifact_output_dir')


def test_gen_loc_schemes_cesr_for_agent_returns_loc_scheme_and_endrole():
    aid = 'test_aid'
    eid = 'test_eid'
    role = kering.Roles.agent
    hab = mock(habbing.Hab)
    kever = mock(eventing.Kever)
    hab.kevers = {aid: kever}
    hab.db = mock(basing.Baser)
    hab.db.ends = mock(koming.Komer)
    when(hab.db.ends).getItemIter(keys=(aid, kering.Roles.agent)).thenReturn([((None, kering.Roles.agent, eid), None)])
    when(hab).loadLocScheme(eid=eid, scheme='').thenReturn(bytearray(b'loc_scheme_data'))
    when(hab).loadEndRole(cid=aid, eid=eid, role=kering.Roles.agent).thenReturn(bytearray(b'end_role_data'))

    msgs = artifacting.gen_loc_schemes_cesr(hab, aid, role=role)
    assert msgs == bytearray(b'loc_scheme_dataend_role_data')
