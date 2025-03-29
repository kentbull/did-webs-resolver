# -*- encoding: utf-8 -*-
"""
dkr.core.didding module

"""

import datetime
import json
import math
import re
import itertools

from base64 import urlsafe_b64encode
from functools import reduce
from keri import kering
from keri.app import oobiing, habbing
from keri.core import coring,scheming
from keri.help import helping
from keri.vdr import credentialing, verifying

DID_KERI_RE = re.compile(r'\Adid:keri:(?P<aid>[^:]+)\Z', re.IGNORECASE)
DID_WEBS_RE = re.compile(r'\Adid:web(s)?:(?P<domain>[^%:]+)(?:%3a(?P<port>\d+))?(?::(?P<path>.+?))?(?::(?P<aid>[^:]+))\Z', re.IGNORECASE)

DID_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DID_TIME_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")

DES_ALIASES_SCHEMA="EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5"

VMETH_FIELD='verificationMethod'

def parseDIDKeri(did):
    match = DID_KERI_RE.match(did)
    if match is None:
        raise ValueError(f"{did} is not a valid did:keri DID")

    aid = match.group("aid")

    try:
        _ = coring.Prefixer(qb64=aid)
    except Exception as e:
        raise ValueError(f"{aid} is an invalid AID")

    return aid

def parseDIDWebs(did):
    match = DID_WEBS_RE.match(did)
    if match is None:
        raise ValueError(f"{did} is not a valid did:web(s) DID")

    domain, port, path, aid = match.group("domain", "port", "path", "aid")

    try:
        _ = coring.Prefixer(qb64=aid)
    except Exception as e:
        raise ValueError(f"{aid} is an invalid AID")

    return domain, port, path, aid


def generateDIDDoc(hby: habbing.Habery, did, aid, oobi=None, meta=False, reg_name=None):
    if (did and aid) and not did.endswith(aid):
        raise ValueError(f"{did} does not end with {aid}")
    print("Generating DID document for", did, "with aid", aid, "using oobi", oobi, "and metadata", meta, "registry name for creds", reg_name)
    
    hab = None
    if aid in hby.habs:
        hab = hby.habs[aid]
    
    if oobi is not None:
        obr = hby.db.roobi.get(keys=(oobi,))
        if obr is None or obr.state == oobiing.Result.failed:
            msg = dict(msg=f"OOBI resolution for did {did} failed.")
            data = json.dumps(msg)
            return data.encode("utf-8")

    kever = None
    if aid in hby.kevers:
        kever = hby.kevers[aid]
    else:
        raise ValueError(f"unknown {aid}")

    vms = []
    for idx, verfer in enumerate(kever.verfers):
        kid = verfer.qb64
        x = urlsafe_b64encode(verfer.raw).rstrip(b'=').decode('utf-8')
        vms.append(dict(
            id=f"#{verfer.qb64}",
            type="JsonWebKey",
            controller=did,
            publicKeyJwk=dict(
                kid=f"{kid}",
                kty="OKP",
                crv="Ed25519",
                x=f"{x}"
            )
        ))

    if isinstance(kever.tholder.thold, int):
        if kever.tholder.thold > 1:
            conditions = [vm.get("id") for vm in vms]
            vms.append(dict(
                id=f"#{aid}",
                type="ConditionalProof2022",
                controller=did,
                threshold=kever.tholder.thold,
                conditionThreshold=conditions
            ))
    elif isinstance(kever.tholder.thold, list):
        lcd = int(math.lcm(*[fr.denominator for fr in kever.tholder.thold[0]]))
        threshold = float(lcd/2)
        numerators = [int(fr.numerator * lcd / fr.denominator) for fr in kever.tholder.thold[0]]
        conditions = []
        for idx, verfer in enumerate(kever.verfers):
            conditions.append(dict(
                condition=vms[idx]['id'],
                weight=numerators[idx]
            ))
        vms.append(dict(
            id=f"#{aid}",
            type="ConditionalProof2022",
            controller=did,
            threshold=threshold,
            conditionWeightedThreshold=conditions
        ))

    x = [(keys[1], loc.url) for keys, loc in
         hby.db.locs.getItemIter(keys=(aid,)) if loc.url]

    witnesses = []
    for idx, eid in enumerate(kever.wits):
        for (tid, scheme), loc in hby.db.locs.getItemIter(keys=(eid,)):
            witnesses.append(dict(
                idx=idx,
                scheme=scheme,
                url=loc.url
            ))
            
    sEnds=[]
    if hab and hasattr(hab, 'fetchRoleUrls'):
        ends = hab.fetchRoleUrls(cid=aid)
        sEnds.extend(addEnds(ends))
        ends = hab.fetchWitnessUrls(cid=aid)
        sEnds.extend(addEnds(ends))

    eq_ids = []
    aka_ids = []
    for s in designatedAliases(hby, aid, reg_name=reg_name):
        if s.startswith("did:webs"):
            eq_ids.append(s)
        aka_ids.append(s)

    diddoc = dict(
        id=did,
        verificationMethod=vms,
        service=sEnds,
        alsoKnownAs=aka_ids
    )

    if meta is True:
        didResolutionMetadata = dict(
            contentType="application/did+json",
            retrieved=helping.nowUTC().strftime(DID_TIME_FORMAT)
        )

        didDocumentMetadata = dict(
            witnesses=witnesses,
            versionId=f"{kever.sner.num}",
            equivalentId=eq_ids,
        )

        resolutionResult = dict(
            didDocument=diddoc,
            didResolutionMetadata=didResolutionMetadata,
            didDocumentMetadata=didDocumentMetadata
        )
        return resolutionResult
    else:
        return diddoc

def toDidWeb(diddoc):
    if diddoc:
        diddoc['id'] = diddoc['id'].replace('did:webs', 'did:web')
        for verificationMethod in diddoc["verificationMethod"]:
            verificationMethod['controller'] = verificationMethod['controller'].replace('did:webs', 'did:web')
        return diddoc

def fromDidWeb(diddoc):
    # Log the original state of the DID and controller
    print(f"fromDidWeb() called with id: {diddoc['id']}")
    initial_controller = diddoc['verificationMethod'][0]['controller']
    print(f"Initial controller in fromDidWeb: {initial_controller}")

    # Apply the replacement only if necessary
    if 'did:web' in diddoc['id'] and 'did:webs' not in diddoc['id']:
        diddoc['id'] = diddoc['id'].replace('did:web', 'did:webs')
        print(f"Updated id in fromDidWeb: {diddoc['id']}")

    for verificationMethod in diddoc['verificationMethod']:
        if 'did:web' in verificationMethod['controller'] and 'did:webs' not in verificationMethod['controller']:
            verificationMethod['controller'] = verificationMethod['controller'].replace('did:web', 'did:webs')
            print(f"Updated controller in fromDidWeb: {verificationMethod['controller']}")

    return diddoc

def designatedAliases(hby: habbing.Habery, aid: str, reg_name: str=None):
    """
    Returns the credentialer for the des-aliases schema, or None if it doesn't exist.
    """
    da_ids = []
    if aid in hby.habs:
        if reg_name is None:
            reg_name = hby.habs[aid].name
        rgy = credentialing.Regery(hby=hby, name=reg_name)
        vry = verifying.Verifier(hby=hby, reger=rgy.reger)
        
        saids = rgy.reger.issus.get(keys=aid)
        scads = rgy.reger.schms.get(keys=DES_ALIASES_SCHEMA)
        # self-attested, there is no issuee, and schmea is designated aliases
        saids = [saider for saider in saids if saider.qb64 in [saider.qb64 for saider in scads]]

        creds = rgy.reger.cloneCreds(saids,hby.habs[aid].db)

        for idx, cred in enumerate(creds):
            sad = cred['sad']
            status = cred["status"]
            if status['et'] == 'iss' or status['et'] == 'bis':
                da_ids.append(sad['a']['ids'])

    return list(itertools.chain.from_iterable(da_ids))

def addEnds(ends):
    def process_role(role):
        return reduce(lambda rs, eids: rs + process_eids(eids, role), ends.getall(role), [])

    def process_eids(eids, role):
        return reduce(lambda es, eid: es + process_eid(eid, eids[eid], role), eids, [])

    def process_eid(eid, val, role):
        v = dict(
            id=f"#{eid}/{role}",
            type=role,
            serviceEndpoint={proto: f"{host}" for proto, host in val.items()}
        )
        return [v]

    return reduce(lambda emit, role: emit + process_role(role), ends, [])
