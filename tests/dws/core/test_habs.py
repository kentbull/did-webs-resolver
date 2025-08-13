import random
import string

from keri.app import habbing
from keri.core import signing

from dws.core import habs


def test_habs():
    # generate a random 6 character string
    cf = habs.get_habery_configer(name=None, base='', head_dir_path=None, temp=True)
    assert cf is None
    cf = habs.get_habery_configer(name='test_habs', base='', head_dir_path=None, temp=True)
    assert cf is not None

    aeid = habs.get_auth_encryption_aid(name='test_habs', base='', temp=True)
    assert aeid is None  # Habery has not been created yet
    random_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # tests the already existing case - needs to set temp=False to check for existing files
    #   WARNING: this makes the test somewhat  flaky
    salt = signing.Salter().qb64
    habbing.Habery(name=random_name, base='', bran=salt, temp=False)
    hby, hby_doer = habs.get_habery_and_doer(name=random_name, base='', bran=salt, cf=cf, temp=False)
    assert hby is not None
    assert hby_doer is not None

    # use random name to avoid LMDB lock table conflicts
    random_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    hby, hby_doer = habs.get_habery_and_doer(name=random_name, base='', bran=None, cf=cf, temp=True)
    assert hby is not None
    assert hby_doer is not None
