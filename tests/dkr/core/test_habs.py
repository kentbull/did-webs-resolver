import random
import string

from keri.app import habbing
from keri.core import signing

from dkr.core import habs


def test_habs():
    # generate a random 6 character string
    cf = habs.get_habery_configer(name=None, base="", head_dir_path=None)
    assert cf is None
    cf = habs.get_habery_configer(name="test_habs", base="", head_dir_path=None)
    assert cf is not None

    aeid = habs.get_auth_encryption_aid(name="test_habs", base="")
    assert aeid is None # Habery has not been created yet
    random_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # tests the already existing case
    salt = signing.Salter().qb64
    hby = habbing.Habery(name=random_name, base="", bran=salt)
    hby, hby_doer = habs.get_habery_and_doer(name=random_name, base="", bran=salt, cf=cf)
    assert hby is not None
    assert hby_doer is not None

    # use random name to avoid LMDB lock table conflicts
    random_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    hby, hby_doer = habs.get_habery_and_doer(name=random_name, base="", bran=signing.Salter().qb64, cf=cf)
    assert hby is not None
    assert hby_doer is not None