from keri.app import configing, habbing, keeping
from keri.app.cli.common import existing


def get_auth_encryption_aid(name: str, base: str):
    """Get the Authentication and Encryption Identifier (AEID) from the Keeper."""
    ks = keeping.Keeper(name=name, base=base, temp=False, reopen=True)
    return ks.gbls.get('aeid')


def get_habery_doer(name: str, base: str, bran: str, cf: configing.Configer = None) -> (habbing.Habery, habbing.HaberyDoer):
    """Get the Habery and its Doer respecting any existing AEID."""
    aeid = get_auth_encryption_aid(name, base)
    if aeid is None:
        hby = habbing.Habery(name=name, base=base, bran=bran, cf=cf)
    else:
        hby = existing.setupHby(name=name, base=base, bran=bran, cf=cf)
    return hby, habbing.HaberyDoer(habery=hby)
