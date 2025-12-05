from keri import kering
from keri.app import habbing

from dws import log_name, ogler

logger = ogler.getLogger(log_name)


def get_resolved_oobi(hby: habbing.Habery, pre: str) -> str | None:
    """Gets a resolved OOBI for a given identifier prefix or None if not found."""
    for (oobi,), obr in hby.db.roobi.getItemIter():
        if obr.cid == pre:
            return oobi
    return None


def generate_oobi(hby: habbing.Habery, pre: str = None, alias: str = None, role: str = kering.Roles.witness):
    if pre:
        hab = hby.habByPre(pre=pre)
    else:
        hab = hby.habByName(name=alias)
    if not hab:
        return None

    oobi = None
    if role in (kering.Roles.witness,):
        if not hab.kever.wits:
            logger.error(f'{alias} identifier {hab.pre} does not have any witnesses.')
            return None
        for wit in hab.kever.wits:
            urls = hab.fetchUrls(eid=wit, scheme=kering.Schemes.http) or hab.fetchUrls(eid=wit, scheme=kering.Schemes.https)
            if not urls:
                logger.error(f'unable to query witness {wit}, no http endpoint')
                return None

            url = urls[kering.Schemes.https] if kering.Schemes.https in urls else urls[kering.Schemes.http]
            oobi = f'{url.rstrip("/")}/oobi/{hab.pre}/witness'
    elif role in (kering.Roles.controller,):
        urls = hab.fetchUrls(eid=hab.pre, scheme=kering.Schemes.http) or hab.fetchUrls(
            eid=hab.pre, scheme=kering.Schemes.https
        )
        if not urls:
            logger.error(f'{alias} identifier {hab.pre} does not have any controller endpoints')
            return None
        url = urls[kering.Schemes.https] if kering.Schemes.https in urls else urls[kering.Schemes.http]
        oobi = f'{url.rstrip("/")}/oobi/{hab.pre}/controller'
    elif role in (kering.Roles.mailbox,):
        for (_, _, eid), end in hab.db.ends.getItemIter(
            keys=(
                hab.pre,
                kering.Roles.mailbox,
            )
        ):
            if not (end.allowed and end.enabled is not False):
                continue

            urls = hab.fetchUrls(eid=eid, scheme=kering.Schemes.http) or hab.fetchUrls(eid=eid, scheme=kering.Schemes.https)
            if not urls:
                logger.error(f'{alias} identifier {hab.pre} does not have any mailbox endpoints')
                return None
            url = urls[kering.Schemes.https] if kering.Schemes.https in urls else urls[kering.Schemes.http]
            oobi = f'{url.rstrip("/")}/oobi/{hab.pre}/mailbox/{eid}'
    return oobi
