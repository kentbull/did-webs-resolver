import pytest
from keri.app.habbing import Habery
from keri.vdr.credentialing import Regery

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
