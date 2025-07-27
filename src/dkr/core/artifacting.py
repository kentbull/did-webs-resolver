import json
import os

from keri.app import habbing
from keri.app.habbing import Habery
from keri.core import serdering
from keri.db import basing
from keri.vdr import credentialing, viring
from keri.vdr.credentialing import Regery

from dkr import log_name, ogler
from dkr.core import didding, ends

logger = ogler.getLogger(log_name)


def gen_kel_cesr(db: basing.Baser, pre: str) -> bytearray:
    """Return a bytearray of the CESR stream of all KEL events for a given prefix."""
    msgs = bytearray()
    for msg in db.clonePreIter(pre=pre):
        msgs.extend(msg)
    return msgs


def make_keri_cesr_path(output_dir: str, aid: str):
    """Create keri.cesr enclosing dir, and any intermediate dirs, if not existing"""
    kc_dir_path = os.path.join(output_dir, aid)
    if not os.path.exists(kc_dir_path):
        logger.debug(f'Creating directory for KERI CESR events: {kc_dir_path}')
        os.makedirs(kc_dir_path)
    return os.path.join(kc_dir_path, f'{ends.KERI_CESR}')


def write_keri_cesr_file(output_dir: str, aid: str, keri_cesr: bytearray):
    """Write the keri.cesr file to output path, making any enclosing directories"""
    kc_file_path = make_keri_cesr_path(output_dir, aid)
    with open(kc_file_path, 'w') as kcf:
        tmsg = keri_cesr.decode('utf-8')
        logger.debug(f'Writing CESR events to {kc_file_path}: \n{tmsg}')
        kcf.write(tmsg)


def get_self_issued_acdcs(aid: str, reger: credentialing.Reger, schema: str = didding.DES_ALIASES_SCHEMA):
    """Get self issued ACDCs filtered by schema"""
    creds_issued = reger.issus.get(keys=aid)
    creds_by_schema = reger.schms.get(keys=schema.encode('utf-8'))

    # self-attested, there is no issuee, and schema is designated aliases
    return [
        cred_issued
        for cred_issued in creds_issued
        if cred_issued.qb64 in [cred_by_schm.qb64 for cred_by_schm in creds_by_schema]
    ]


def gen_tel_cesr(reger: viring.Reger, regk: str) -> bytearray:
    """Get the CESR stream of TEL events for a given registry."""
    msgs = bytearray()
    for msg in reger.clonePreIter(pre=regk):
        msgs.extend(msg)
    return msgs


def gen_acdc_cesr(hab: habbing.Hab, creder: serdering.SerderACDC) -> bytearray:
    """Add the CESR stream of the self attestation ACDCs for the given AID including signatures."""
    return hab.endorse(creder)


def gen_des_aliases_cesr(
    hab: habbing.Hab, reger: credentialing.Reger, aid: str, schema: str = didding.DES_ALIASES_SCHEMA
) -> bytearray:
    """
    Select a specific ACDC from the local registry (Regery), if it exists, to generate the
    CESR stream
    Args:
        hab: The local Hab to use for generating the CESR stream
        aid: AID prefix to retrieve the ACDC for
        reger: The Regery to use for retrieving the ACDC
        schema: the schema to use to select the target ACDC from the local registry

    Returns:
        bytearray: CESR stream of locally stored ACDC events for the specified AID and schema
    """
    # self-attested, there is no issuee, and schema is designated aliases
    local_creds = get_self_issued_acdcs(aid, reger, schema)

    msgs = bytearray()
    for cred in local_creds:
        creder, *_ = reger.cloneCred(said=cred.qb64)
        if creder.regi is not None:
            # TODO check if this works if we only get the regi CESR stream once
            msgs.extend(gen_tel_cesr(reger, creder.regi))
            msgs.extend(gen_tel_cesr(reger, creder.said))
        msgs.extend(gen_acdc_cesr(hab, creder))
    return msgs


def make_did_json_path(output_dir: str, aid: str):
    """Create the directory (and any intermediate directories in the given path) if it doesn't already exist"""
    dd_dir_path = os.path.join(output_dir, aid)
    if not os.path.exists(dd_dir_path):
        os.makedirs(dd_dir_path)
    return dd_dir_path


def write_did_json_file(dd_dir_path: str, diddoc: dict, meta: bool = False):
    """save did.json to a file at output_dir/{aid}/{AID}.json"""
    dd_file_path = os.path.join(dd_dir_path, f'{ends.DID_JSON}')
    with open(dd_file_path, 'w') as ddf:
        json.dump(didding.to_did_web(diddoc, meta), ddf)


def generate_artifacts(hby: Habery, rgy: Regery, did: str, meta: bool = False, output_dir: str = '.'):
    domain, port, path, aid, query = didding.parse_did_webs(did)

    # generate did doc
    did_json = didding.generate_did_doc(hby, did=did, aid=aid, oobi=None, meta=meta)
    if did_json is None:
        logger.error('DID document failed to generate')
        return None, None
    # Create the directory (and any intermediate directories in the given path) if it doesn't already exist
    dd_dir_path = make_did_json_path(output_dir, aid)
    write_did_json_file(dd_dir_path, did_json, meta)

    logger.info(f'Generating CESR event stream data from local Habery keystore')
    hab = hby.habs[aid]
    reger = rgy.reger
    keri_cesr = bytearray()
    keri_cesr.extend(gen_kel_cesr(hby.db, aid))  # add KEL CESR stream
    keri_cesr.extend(gen_des_aliases_cesr(hab, reger, aid))  # add designated aliases TELs and ACDCs
    write_keri_cesr_file(output_dir, aid, keri_cesr)

    return did_json, keri_cesr
