from typing import List

from hio.base import doing, Doer
from hio.help import decking
from hio.help.decking import Deck
from keri import kering
from keri.app import habbing, oobiing
from keri.app.agenting import Receiptor, WitnessReceiptor
from keri.app.delegating import Anchorer
from keri.app.forwarding import Poster
from keri.app.habbing import Habery, Hab
from keri.core.coring import Seqner
from keri.db import basing
from keri.db.basing import Baser
from keri.help import helping


def delegate_confirm_single_sig(del_deeds, dgt_deeds, wit_deeds):
    """
    Perform single sig delegation approval; equivalent of `kli delegate confirm`
    Uses deeds created from a Doist in the context of a test.
    """

class HabHelpers:
    @staticmethod
    def generate_oobi(hby: habbing.Habery, alias: str = None, role: str = kering.Roles.witness):
        hab = hby.habByName(name=alias)
        oobi = ''
        if role in (kering.Roles.witness,):
            if not hab.kever.wits:
                raise kering.ConfigurationError(f"{alias} identifier {hab.pre} does not have any witnesses.")
            for wit in hab.kever.wits:
                urls = hab.fetchUrls(eid=wit, scheme=kering.Schemes.http) \
                       or hab.fetchUrls(eid=wit, scheme=kering.Schemes.https)
                if not urls:
                    raise kering.ConfigurationError(f"unable to query witness {wit}, no http endpoint")

                url = urls[kering.Schemes.https] if kering.Schemes.https in urls else urls[kering.Schemes.http]
                oobi = f"{url.rstrip("/")}/oobi/{hab.pre}/witness"
        elif role in (kering.Roles.controller,):
            urls = hab.fetchUrls(eid=hab.pre, scheme=kering.Schemes.http) \
                   or hab.fetchUrls(eid=hab.pre, scheme=kering.Schemes.https)
            if not urls:
                raise kering.ConfigurationError(f"{alias} identifier {hab.pre} does not have any controller endpoints")
            url = urls[kering.Schemes.https] if kering.Schemes.https in urls else urls[kering.Schemes.http]
            oobi = f"{url.rstrip("/")}/oobi/{hab.pre}/controller"
        elif role in (kering.Roles.mailbox,):
            for (_, _, eid), end in hab.db.ends.getItemIter(keys=(hab.pre, kering.Roles.mailbox, )):
                if not (end.allowed and end.enabled is not False):
                    continue

                urls = hab.fetchUrls(eid=eid, scheme=kering.Schemes.http) or hab.fetchUrls(eid=hab.pre,
                                                                                           scheme=kering.Schemes.https)
                if not urls:
                    raise kering.ConfigurationError(f"{alias} identifier {hab.pre} does not have any mailbox endpoints")
                url = urls[kering.Schemes.https] if kering.Schemes.https in urls else urls[kering.Schemes.http]
                oobi = f"{url.rstrip("/")}/oobi/{hab.pre}/mailbox/{eid}"
        if oobi:
            return oobi
        else:
            raise kering.ConfigurationError(f"Unable to generate OOBI for {alias} identifier {hab.pre} with role {role}")

    @staticmethod
    def resolve_wit_oobi(doist: doing.Doist, wit_deeds: List[Doer], hby: habbing.Habery, oobi: str, alias: str = None):
        """Resolve an OOBI depending on a given witness for a given Habery."""
        obr = basing.OobiRecord(date=helping.nowIso8601())
        if alias is not None:
            obr.oobialias = alias
        hby.db.oobis.put(keys=(oobi,), val=obr)

        oobiery = oobiing.Oobiery(hby=hby)
        authn = oobiing.Authenticator(hby=hby)
        oobiery_deeds = doist.enter(doers=oobiery.doers + authn.doers)
        while not oobiery.hby.db.roobi.get(keys=(oobi,)):
            doist.recur(deeds=decking.Deck(wit_deeds + oobiery_deeds))
            hby.kvy.processEscrows()  # process any escrows from witness receipts

    @staticmethod
    def has_delegables(db: Baser):
        dlgs = []
        for (pre, sn), edig in db.delegables.getItemIter():
            dlgs.append((pre, sn, edig))
        return dlgs

class DelegationAutoApprover(doing.Doer):
    """
    Automatically approves delegation requests for testing purposes.
    """
    def __init__(self):
        super(DelegationAutoApprover, self).__init__()

    def recur(self, tock=0.0, **opts):
        pass


class Dipper(doing.DoDoer):
    """
    Handles the delegation lifecycle for single-sig identifiers from the perspective of the delegate.

    Assumes the delegate Hab is already made and that only witness receipts, delegation approval, and
    waiting for completion are needed.
    """
    def __init__(self, hby: Habery, hab: Hab, proxy: str = None, endpoint: str = None):
        self.hby = hby
        self.hab = hab
        self.proxy = self.hby.habByName(proxy) if proxy is not None else None
        self.sender = proxy if proxy is not None else hab
        self.endpoint = endpoint
        self.postman = Poster(hby=self.hby)
        self.cues = decking.Deck()

        # Doers
        self.anchorer = Anchorer(hby=self.hby, proxy=self.proxy)
        self.icpCompleter = DipCompleter(self.anchorer, self.hab, self.cues)
        # TODO maybe witReceiptor and receiptor are not needed since the Anchorer makes its own?
        self.witReceiptor = WitnessReceiptor(hby=self.hby)
        self.receiptor = Receiptor(hby=self.hby)
        self.receiptWaiter = ReceiptWaiter(pre=self.hab.pre, sn=0, cues=self.cues, endpoint=self.endpoint,
                                           witReceiptor = self.witReceiptor, receiptor=self.receiptor)
        self.dipSender = DipSender(hab=self.hab, sender=self.sender, cues=self.cues, postman=self.postman)
        doers: List[Doer] = [self.icpCompleter, self.witReceiptor, self.receiptor, self.postman, self.dipSender]
        if hab.kever.wits:
            doers.append(self.receiptWaiter)
        super(Dipper, self).__init__(doers=doers)

    def recur(self, tyme, deeds=None):
        if self.cues:
            for cue in self.cues:
                kin = cue.get("kin", "")
                if kin == "dipSent":
                    print(f"Delegated inception process complete for {self.hab.pre}.")
                    self.remove(self.doers)  # remove any remaining doers
                    return True  # done
        super(Dipper, self).recur(tyme, deeds=deeds)
        return False  # not done yet

class ReceiptWaiter(doing.Doer):
    """
    Waits for a receiptor to finish receipting and then publishes a receipt completion cue.
    """
    def __init__(self, pre: str, sn: int, cues: decking.Deck, endpoint: str,
                 witReceiptor: WitnessReceiptor, receiptor: Receiptor):
        self.pre = pre
        self.sn = sn
        self.cues = cues
        self.endpoint = endpoint
        self.witReceiptor = witReceiptor
        self.receiptor = receiptor
        super(ReceiptWaiter, self).__init__()

    def waitOnReceipts(self):
        """Uses Receiptor to propagage """
        if self.endpoint:
            yield from self.receiptor.receipt(pre=self.pre, sn=self.sn)
        else:
            self.witReceiptor.msgs.append(dict(pre=self.pre))
            while not self.witReceiptor.cues:
                _ = yield self.tock

    def recur(self, tock=0.0, **opts):
        while True:
            while self.cues:
                cue = self.cues.popleft()
                cueKin = cue["kin"]
                if cueKin == "delComplete":
                    yield from self.waitOnReceipts()
                    print(f"Receipts obtained for {self.pre} at sn {self.sn}, cueing completion.")
                    self.cues.append({'cueKin': 'rctComplete', 'pre': self.pre, 'sn': self.sn})
                    return True
                yield tock
            yield tock

class DipSender(doing.Doer):
    """
    Sends the delegated inception event to the delegator.
    """
    def __init__(self, hab: Hab, sender: str, cues: Deck, postman: Poster):
        self.hab = hab
        self.sender = sender
        self.cues = cues
        self.postman = postman
        super(DipSender, self).__init__()

    def sendDip(self):
        yield from self.postman.sendEventToDelegator(
            hab=self.hab,
            sender=self.sender,
            fn=self.hab.kever.sn)

    def recur(self, tock=0.0, **opts):
        while True:
            while self.cues:
                cue = self.cues.popleft()
                cueKin = cue["kin"]
                if cueKin == "rctComplete":
                    print(f"Sending delegated inception event for {self.hab.pre} to delegator...")
                    yield from self.sendDip()
                    self.cues.append({'kin': 'dipSent', 'pre': self.hab.pre})
                    return True
                yield tock
            yield tock

class DipCompleter(doing.Doer):
    """
    Completes the delegated inception process by waiting for delegation approval.
    """
    def __init__(self, anchorer: Anchorer, hab: Hab, cues: Deck):
        self.anchorer = anchorer
        self.hab = hab
        self.cues = cues
        super(DipCompleter, self).__init__()

    def recur(self, tock=0.0, **opts):
        self.anchorer.delegation(pre=self.hab.pre, sn=0)
        print(f"Waiting for delegation approval for {self.hab.kever.prefixer.qb64}...")
        while not self.anchorer.complete(self.hab.kever.prefixer, Seqner(sn=self.hab.kever.sn)):
            yield self.tock
        print(f"Delegation approved for {self.hab.kever.prefixer.qb64}, cueing completion.")
        self.cues.append({'kin': 'delComplete', 'pre': self.hab.pre})
        return True


