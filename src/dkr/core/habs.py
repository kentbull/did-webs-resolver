from keri.app import configing, habbing, keeping
from keri.app.cli.common import existing


def get_habery_configer(name: str | None, base: str | None, head_dir_path: str | None, temp: bool = False):
    """Get the Configer for the Habery if name provide otherwise return None."""
    if name is not None:
        return configing.Configer(name=name, base=base, headDirPath=head_dir_path, temp=temp, reopen=True, clear=False)
    return None


def get_auth_encryption_aid(name: str, base: str, temp: bool = False):
    """Get the Authentication and Encryption Identifier (AEID) from the Keeper."""
    ks = keeping.Keeper(name=name, base=base, temp=temp, reopen=True)
    aeid = ks.gbls.get('aeid')
    ks.close()  # to avoid LMDB reader table locks
    return aeid


def get_habery_and_doer(
    name: str | None, base: str | None, bran: str | None, cf: configing.Configer = None, temp: bool = False
) -> (habbing.Habery, habbing.HaberyDoer):
    """Get the Habery and its Doer respecting any existing AEID."""
    aeid = get_auth_encryption_aid(name, base)
    if aeid is None:
        hby = habbing.Habery(name=name, base=base, bran=bran, cf=cf, temp=temp)
    else:
        hby = existing.setupHby(name=name, base=base, bran=bran, cf=cf, temp=temp)
    return hby, habbing.HaberyDoer(habery=hby)
