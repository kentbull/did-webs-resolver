"""
Configure PyTest

Use this module to configure pytest
https://docs.pytest.org/en/latest/pythonpath.html

"""
import json
from typing import Union

import pytest
from hio.base import doing
from keri.app import habbing, grouping
from keri.core import scheming, coring, eventing, serdering
from keri.help import helping
from keri.vdr import credentialing, verifying


@pytest.fixture()
def mock_helping_now_utc(monkeypatch):
    """
    Replace nowUTC universally with fixed value for testing
    """

    def mock_now_utc():
        """
        Use predetermined value for now (current time)
        '2021-01-01T00:00:00.000000+00:00'
        """
        return helping.fromIso8601('2021-01-01T00:00:00.000000+00:00')

    monkeypatch.setattr(helping, 'nowUTC', mock_now_utc)


def assemble_did_webs_did(domain, aid, port=None, path=None):
    did = f'did:webs:{domain}{port}'
    if port:
        did += f'%3a{port}'
    if path:
        did += f':{path}'
    if aid:
        did += f':{aid}'
    return did


def assemble_did_web_did(domain, aid, port=None, path=None):
    did = f'did:web:{domain}'
    if port:
        did += f'%3a{port}'
    if path:
        did += f':{path}'
    if aid:
        did += f':{aid}'
    return did

class TestHelpers:
    @staticmethod
    def add_cred_to_aid(hby: habbing.Habery, hab: habbing.Hab,
                        schema_said: str,
                        schema_json: dict,
                        subject_data: dict,
                        rules_json: dict,
                        source: Union[dict, list] = None,
                        recp: str = None,
                        registry_nonce: str = None,
                        private: bool=False,
                        private_credential_nonce: str = None,
                        private_subject_nonce: str = None
                        ):
        # Components needed for issuance
        hby_doer = habbing.HaberyDoer(habery=hby)
        regery = credentialing.Regery(hby=hby, name=hab.name, temp=hby.temp)
        counselor = grouping.Counselor(hby=hby)
        registrar = credentialing.Registrar(hby=hby, rgy=regery, counselor=counselor)
        verifier = verifying.Verifier(hby=hby, reger=regery.reger)
        credentialer = credentialing.Credentialer(hby=hby, rgy=regery, registrar=registrar, verifier=verifier)
        regery_doer = credentialing.RegeryDoer(rgy=regery)

        # set up Doist to run doers
        doist = doing.Doist(limit=1.0, tock=0.03125, real=True)
        deeds = doist.enter(doers=[hby_doer, counselor, registrar, credentialer, regery_doer])

        # Add schema to resolver schema cache
        schemer = scheming.Schemer(
            raw=bytes(json.dumps(schema_json), 'utf-8'), typ=scheming.JSONSchema(), code=coring.MtrDex.Blake3_256
        )
        cache = scheming.CacheResolver(db=hby.db)
        cache.add(schemer.said, schemer.raw)

        # Create registry
        issuer_reg = regery.makeRegistry(prefix=hab.pre, name=hab.name, noBackers=True, nonce=registry_nonce)
        rseal = eventing.SealEvent(issuer_reg.regk, '0', issuer_reg.regd)._asdict()
        reg_anc = hab.interact(data=[rseal])
        reg_anc_serder = serdering.SerderKERI(raw=bytes(reg_anc))
        registrar.incept(iserder=issuer_reg.vcp, anc=reg_anc_serder)

        while not registrar.complete(pre=issuer_reg.regk, sn=0):
            doist.recur(deeds=deeds)  # run until registry is incepted

        assert issuer_reg.regk in regery.reger.tevers

        # Create and issue the self-attested credential
        creder = credentialer.create(
            regname=issuer_reg.name,
            recp=recp,
            schema=schema_said,
            source=source,
            rules=rules_json,
            data=subject_data,
            private=private,
            private_credential_nonce=private_credential_nonce,
            private_subject_nonce=private_subject_nonce,
        )

        # Create ACDC issuance and anchor to KEL
        reg_iss_serder = issuer_reg.issue(said=creder.said, dt=creder.attrib['dt'])
        iss_seal = eventing.SealEvent(reg_iss_serder.pre, '0', reg_iss_serder.said)._asdict()
        iss_anc = hab.interact(data=[iss_seal])
        anc_serder = serdering.SerderKERI(raw=iss_anc)
        credentialer.issue(creder, reg_iss_serder)
        registrar.issue(creder, reg_iss_serder, anc_serder)

        while not credentialer.complete(said=creder.said):
            doist.recur(deeds=deeds)
            verifier.processEscrows()

        state = issuer_reg.tever.vcState(vci=creder.said)
        assert state.et == coring.Ilks.iss
        return creder, reg_iss_serder, anc_serder