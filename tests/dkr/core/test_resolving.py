import json
import urllib.parse

import falcon
import pytest
from falcon import testing
from hio.base import doing
from keri.app import grouping, habbing, oobiing
from keri.core import coring, eventing, scheming, serdering
from keri.vdr import credentialing, verifying

from dkr.core import didding, resolving
from dkr.core.ends import monitoring
from tests.conftest import assemble_did_web_did, assemble_did_webs_did, TestHelpers


def test_health_end():
    """Simple test to demonstrate Falcon HTTP endpoint testing."""
    app = resolving.falcon_app()
    app.add_route('/health', monitoring.HealthEnd())

    client = testing.TestClient(app=app)

    rep = client.simulate_get('/health')
    assert rep.status == falcon.HTTP_200
    assert rep.content_type == falcon.MEDIA_JSON
    assert 'Health is okay' in rep.text


def self_attested_aliases_cred_subj(domain: str, aid: str, port: str = None, path: str = None):
    """
    Generate test self attested credential data using the domain, AID, port, path, and assembler functions.

    Parameters:
        domain (str): domain for did:webs DID
        aid (str): alias identifier for did:webs DID
        port (str): optional port for did:webs DID
        path (str): optional path for did:webs DID
    """
    return dict(
        d='',
        dt='2025-07-24T16:21:40.802473+00:00',  # using fixed date so ACDC SAID stays the same
        ids=[
            assemble_did_web_did(domain, aid, port, path),
            assemble_did_webs_did(domain, aid, port, path),
            assemble_did_web_did('example.com', aid, None, None),
            assemble_did_web_did('foo.com', aid, None, None),
            assemble_did_webs_did('foo.com', aid, None, None),
        ],
    )


@pytest.mark.timeout(3)
def test_resolver_with_did_webs_did_returns_correct_doc():
    """
    Tests generation of both did:webs and did:keri DID Documents and a CESR stream for the did:webs DID.
    Uses static salt, registry nonce, and ACDC datetimestamp for deterministic results.
    """
    salt = b'0ACB-gtnUTQModt9u_UC3LFQ'
    registry_nonce = '0AC-D5XhLUkO-ODnrJMSRPqv'
    with habbing.openHab(salt=salt, name='water', transferable=True, temp=True) as (hby, hab):
        hby_doer = habbing.HaberyDoer(habery=hby)
        aid = 'EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU'
        host = '127.0.0.1'
        port = f'7677'
        did_path = 'dws'
        meta = False
        # fmt: off
        did_webs_did = f'did:webs:{host}%3A{port}:{did_path}:{aid}'         # did:webs:127.0.0.1%3A7677:dws:EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU
        did_keri_did = f'did:keri:{aid}'                                    # did:keri:EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU
        did_json_url = f'http://{host}:{port}/{did_path}/{aid}/did.json'    # http://127.0.0.1:7677/dws/EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU/did.json
        keri_cesr_url = f'http://{host}:{port}/{did_path}/{aid}/keri.cesr'  # http://127.0.0.1:7677/dws/EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU/keri.cesr
        # fmt: on

        # Components needed for issuance
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
        raw_schema = json.loads(open('./local/schema/designated-aliases-public-schema.json', 'rb').read())
        schemer = scheming.Schemer(
            raw=bytes(json.dumps(raw_schema), 'utf-8'), typ=scheming.JSONSchema(), code=coring.MtrDex.Blake3_256
        )
        cache = scheming.CacheResolver(db=hby.db)
        cache.add(schemer.said, schemer.raw)

        # Create registry for designated aliases credential

        issuer_reg = regery.makeRegistry(prefix=hab.pre, name=hab.name, noBackers=True, nonce=registry_nonce)
        rseal = eventing.SealEvent(issuer_reg.regk, '0', issuer_reg.regd)._asdict()
        reg_anc = hab.interact(data=[rseal])
        reg_anc_serder = serdering.SerderKERI(raw=bytes(reg_anc))
        registrar.incept(iserder=issuer_reg.vcp, anc=reg_anc_serder)

        while not registrar.complete(pre=issuer_reg.regk, sn=0):
            doist.recur(deeds=deeds)  # run until registry is incepted

        assert issuer_reg.regk in regery.reger.tevers

        # Create and issue the self-attested credential
        credSubject = self_attested_aliases_cred_subj(host, aid, port, did_path)
        rules = json.loads(open('./local/schema/rules/desig-aliases-public-schema-rules.json', 'rb').read())
        creder = credentialer.create(
            regname=issuer_reg.name,
            recp=None,
            schema='EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5',  # Designated Aliases Public Schema
            source=None,
            rules=rules,
            data=credSubject,
            private=False,
            private_credential_nonce=None,
            private_subject_nonce=None,
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

        # get
        # reger = regery.reger
        # keri_cesr = bytearray()
        # # self.retrieve_kel_via_oobi() # not currently used; an alternative to relying on a local KEL keystore
        # keri_cesr.extend(artifacting.gen_kel_cesr(hby.db, aid))  # add KEL CESR stream
        # keri_cesr.extend(artifacting.gen_des_aliases_cesr(hab, reger, aid))
        #
        did_webs_diddoc = didding.generate_did_doc(hby, did=did_webs_did, aid=aid, oobi=None, meta=meta)

        # Mock load_url to return the did.json and keri.cesr content
        def mock_load_url(url):
            if url == did_json_url:
                # whitespace added for readability - this is just bytes and the whitespace does not impact the actual content
                return (
                    b'{'
                    b'"id": "did:webs:127.0.0.1%3A7677:dws:EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU", '
                    b'"verificationMethod": [{'
                    b'"id": "#DHfhTX8nqUdiU2yw5gnx3dFguwAPiR0SzK4I9ugjRoRF", '
                    b'"type": "JsonWebKey", '
                    b'"controller": "did:webs:127.0.0.1%3A7677:dws:EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU", '
                    b'"publicKeyJwk": {"kid": "DHfhTX8nqUdiU2yw5gnx3dFguwAPiR0SzK4I9ugjRoRF", "kty": "OKP", "crv": "Ed25519", "x": "d-FNfyepR2JTbLDmCfHd0WC7AA-JHRLMrgj26CNGhEU"}}], '
                    b'"service": [], '
                    b'"alsoKnownAs": []}'
                )
            elif url == keri_cesr_url:
                # whitespace added for readability - this is just bytes and the whitespace does not impact the actual content
                return (
                    b'{"v":"KERI10JSON00012b_","t":"icp",'
                    b'"d":"EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"i":"EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"s":"0",'
                    b'"kt":"1","k":["DHfhTX8nqUdiU2yw5gnx3dFguwAPiR0SzK4I9ugjRoRF"],'
                    b'"nt":"1","n":["EDklD8WWC8ks7U-pdxI_hoftybqLVRTj3KJK70jkq6Ha"],'
                    b'"bt":"0","b":[],"c":[],"a":[]}'
                    b'-VAn-AABAAAVeuv7YV_mWaMsye6tH5-G1x58jyJyPJtNePHS3u6vn5UYMlWBFzShMSabVqAtRvW8YW18uEhEGOaZ-cGkcE0J-EAB0AAAAAAAAAAAAAAAAAAAAAAA1AAG2025-07-24T16c27c22d019596p00c00'
                    b'{"v":"KERI10JSON00013a_","t":"ixn",'
                    b'"d":"EHZquNk1-N_KYQJcdXy_jym_YnwlzvdC_6YmGKp6VvIN",'
                    b'"i":"EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"s":"1","p":"EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"a":[{"i":"EK_yp-mT-9YFKVqyUnqAN0CXUd6cxUGeIvem5I0A8TLb","s":"0","d":"EK_yp-mT-9YFKVqyUnqAN0CXUd6cxUGeIvem5I0A8TLb"}]}'
                    b'-VAn-AABAAAfWrHVECbYrHe5hBQnIdgbbwmNPUO4VFsV0HG9zSwmbA-Qc7PqkQCD3IAZ_CnP5RrV2R_MgeYZtFu7PPwdWw0J-EAB0AAAAAAAAAAAAAAAAAAAAAAB1AAG2025-07-24T16c27c22d043008p00c00'
                    b'{"v":"KERI10JSON00013a_","t":"ixn",'
                    b'"d":"EEy7aFHQPBagfqW4MatcUVRVN7yJfft-3RhTzgZvN3Pf",'
                    b'"i":"EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"s":"2","p":"EHZquNk1-N_KYQJcdXy_jym_YnwlzvdC_6YmGKp6VvIN",'
                    b'"a":[{"i":"EAKC8atqn7nuqB7Iqv_FohuGJz6l3ZhWsISbkQFD522D","s":"0","d":"EHFeHZKRISML75268kN2XvkFueHu-mXj3YZAWU8aQxQQ"}]}'
                    b'-VAn-AABAADnenNyGDisXGeZdQCLSzXl9QoYgBxi7cdYw3baY5ukUonbnIQnUBFBsCqPVvrp_dNibpTPVOWtJSDYNglDTKIH-EAB0AAAAAAAAAAAAAAAAAAAAAAC1AAG2025-07-24T16c53c32d268075p00c00'
                    b'{"v":"KERI10JSON0000ff_","t":"vcp",'
                    b'"d":"EK_yp-mT-9YFKVqyUnqAN0CXUd6cxUGeIvem5I0A8TLb",'
                    b'"i":"EK_yp-mT-9YFKVqyUnqAN0CXUd6cxUGeIvem5I0A8TLb",'
                    b'"ii":"EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"s":"0","c":["NB"],"bt":"0","b":[],"n":"0AC-D5XhLUkO-ODnrJMSRPqv"}'
                    b'-VAS-GAB0AAAAAAAAAAAAAAAAAAAAAABEHZquNk1-N_KYQJcdXy_jym_YnwlzvdC_6YmGKp6VvIN'
                    b'{"v":"KERI10JSON0000ed_","t":"iss",'
                    b'"d":"EHFeHZKRISML75268kN2XvkFueHu-mXj3YZAWU8aQxQQ",'
                    b'"i":"EAKC8atqn7nuqB7Iqv_FohuGJz6l3ZhWsISbkQFD522D",'
                    b'"s":"0","ri":"EK_yp-mT-9YFKVqyUnqAN0CXUd6cxUGeIvem5I0A8TLb","dt":"2025-07-24T16:21:40.802473+00:00"}'
                    b'-VAS-GAB0AAAAAAAAAAAAAAAAAAAAAACEEy7aFHQPBagfqW4MatcUVRVN7yJfft-3RhTzgZvN3Pf'
                    b'{"v":"ACDC10JSON0005f4_",'
                    b'"d":"EAKC8atqn7nuqB7Iqv_FohuGJz6l3ZhWsISbkQFD522D",'
                    b'"i":"EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"ri":"EK_yp-mT-9YFKVqyUnqAN0CXUd6cxUGeIvem5I0A8TLb",'
                    b'"s":"EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5",'
                    b'"a":{'
                    b'"d":"EP75lC-MDk8br72V7r5hxY1S7E7U4pgnsGX2WmGyLPxs",'
                    b'"dt":"2025-07-24T16:21:40.802473+00:00",'
                    b'"ids":['
                    b'"did:web:127.0.0.1%3a7677:dws:EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"did:webs:127.0.0.17677%3a7677:dws:EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"did:web:example.com:EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"did:web:foo.com:EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"did:webs:foo.comNone:EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU"]},'
                    b'"r":{'
                    b'"d":"EEVTx0jLLZDQq8a5bXrXgVP0JDP7j8iDym9Avfo8luLw",'
                    b'"aliasDesignation":{"l":"The issuer of this ACDC designates the identifiers in the ids field as the only allowed namespaced aliases of the issuer\'s AID."},'
                    b'"usageDisclaimer":{"l":"This attestation only asserts designated aliases of the controller of the AID, that the AID controlled namespaced alias has been designated by the controller. It does not assert that the controller of this AID has control over the infrastructure or anything else related to the namespace other than the included AID."},'
                    b'"issuanceDisclaimer":{"l":"All information in a valid and non-revoked alias designation assertion is accurate as of the date specified."},'
                    b'"termsOfUse":{"l":"Designated aliases of the AID must only be used in a manner consistent with the expressed intent of the AID controller."}}}'
                    b'-VA0-FABEMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU0AAAAAAAAAAAAAAAAAAAAAAAEMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU-AABAAC29a0oQ7ML0dKq_MNsEUElt7d49KH2-folu9qiHztbLbtHfAU5O1X99TbnExPncL8uW2_mVD9ChYk5fZOK-eMO'
                )
            else:
                raise ValueError(f'Unexpected URL: {url}')

        app = resolving.falcon_app()
        oobiery = oobiing.Oobiery(hby=hby)
        resolver_end = resolving.UniversalResolverResource(hby=hby, oobiery=oobiery, load_url=mock_load_url)
        app.add_route('/1.0/identifiers/{did}', resolver_end)
        client = testing.TestClient(app=app)

        encoded_did_webs = urllib.parse.quote(
            did_webs_did
        )  # to simulate what HIO does to the DID with urllib.parse.quote in Server.buildEnviron

        # Verify did:webs DID doc
        did_webs_response = client.simulate_get(f'/1.0/identifiers/{encoded_did_webs}')

        assert did_webs_response.content_type == 'application/did+ld+json', 'Content-Type should be application/did+ld+json'
        response_diddoc = json.loads(did_webs_response.content)
        assert response_diddoc == did_webs_diddoc, 'did:webs response did document does not match expected diddoc'

        # Verify did:keri DID doc
        encoded_did_keri = urllib.parse.quote(
            did_keri_did
        )  # to simulate what HIO does to the DID with urllib.parse.quote in Server.buildEnviron
        did_keri_response = client.simulate_get(f'/1.0/identifiers/{encoded_did_keri}')

        assert did_keri_response.content_type == 'application/did+ld+json', 'Content-Type should be application/did+ld+json'
        response_diddoc = json.loads(did_keri_response.content)
        did_keri_diddoc = didding.generate_did_doc(hby, did=did_keri_did, aid=aid, oobi=None, meta=meta)
        assert response_diddoc == did_keri_diddoc, 'did:keri response did document does not match expected diddoc'

        # dd, dd_actual = resolving.compare_did_docs(hby=vhby, did=did_webs, aid=aid, dd_res=rdd, kc_res=rkc)
        # assert dd[didding.DD_FIELD][didding.VMETH_FIELD] != did_web_dd[didding.VMETH_FIELD]
        # assert dd[didding.DD_FIELD][didding.VMETH_FIELD] == dd_actual[didding.VMETH_FIELD]

        # no metadata
        # vresult = resolving.verify(dd, dd_actual, meta=False)
        # assert vresult[didding.VMETH_FIELD] == dd[didding.DD_FIELD][didding.VMETH_FIELD]

        # metadata
        # vresult = resolving.verify(dd, dd_actual, meta=True)
        # assert vresult[didding.DD_FIELD][didding.VMETH_FIELD] == dd[didding.DD_FIELD][didding.VMETH_FIELD]

        # should not verify
        # dd_actual_bad = dd_actual
        # remove the last character of the id
        # dd_actual_bad[didding.VMETH_FIELD][0]['id'] = dd_actual_bad[didding.VMETH_FIELD][0]['id'][:-1]
        # vresult = resolving.verify(dd, dd_actual_bad, meta=True)
        # assert vresult[didding.DID_RES_META_FIELD]['error'] == 'notVerified'

        # TODO test services, alsoKnownAs, etc.

        # TODO test a resolution failure
        # if didding.DID_RES_META_FIELD in vresult:
        #     if vresult[didding.DID_RES_META_FIELD]['error'] == 'notVerified':
        #         assert False, "DID verification failed"

        # doist.exit()

        """Done Test"""

@pytest.mark.timeout(60)
def test_resolver_with_metadata_returns_correct_doc():
    """
    Tests generation of both did:webs and did:keri DID Documents and a CESR stream for the did:webs DID with metadata.
    Uses static salt, registry nonce, and ACDC datetimestamp for deterministic results.
    """
    salt = b'0ACB-gtnUTQModt9u_UC3LFQ'
    registry_nonce = '0AC-D5XhLUkO-ODnrJMSRPqv'
    with habbing.openHab(salt=salt, name='water', transferable=True, temp=True) as (hby, hab):
        hby_doer = habbing.HaberyDoer(habery=hby)
        aid = 'EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU'
        host = '127.0.0.1'
        port = f'7677'
        did_path = 'dws'
        meta = True
        # fmt: off
        did_webs_did = f'did:webs:{host}%3A{port}:{did_path}:{aid}?meta=true'         # did:webs:127.0.0.1%3A7677:dws:EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU?meta=true
        did_keri_did = f'did:keri:{aid}'                                    # did:keri:EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU
        did_json_url = f'http://{host}:{port}/{did_path}/{aid}/did.json?meta=true'    # http://127.0.0.1:7677/dws/EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU/did.json?meta=true
        keri_cesr_url = f'http://{host}:{port}/{did_path}/{aid}/keri.cesr'            # http://127.0.0.1:7677/dws/EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU/keri.cesr
        # fmt: on

        schema_json = json.loads(open('./local/schema/designated-aliases-public-schema.json', 'rb').read())
        rules_json = json.loads(open('./local/schema/rules/desig-aliases-public-schema-rules.json', 'rb').read())
        subject_data = self_attested_aliases_cred_subj(host, aid, port, did_path)
        TestHelpers.add_cred_to_aid(
            hby=hby,
            hab=hab,
            schema_said='EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5',  # Designated Aliases Public Schema
            schema_json=schema_json,
            subject_data=subject_data,
            rules_json=rules_json,
            recp=None, # No recipient for self-attested credential
            registry_nonce=registry_nonce
        )

        did_webs_diddoc = didding.generate_did_doc(hby, did=did_webs_did, aid=aid, oobi=None, meta=meta)


        # Mock load_url to return the did.json and keri.cesr content
        def mock_load_url(url):
            if url == did_json_url:
                # whitespace added for readability - this is just bytes and the whitespace does not impact the actual content
                # fmt: off
                return (
                    b'{'
                    b'"didDocument": {'
                        b'"id": "did:webs:127.0.0.1%3A7677:dws:EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU?meta=true", '
                        b'"verificationMethod": [{'
                            b'"id": "#DHfhTX8nqUdiU2yw5gnx3dFguwAPiR0SzK4I9ugjRoRF", '
                            b'"type": "JsonWebKey", '
                            b'"controller": "did:webs:127.0.0.1%3A7677:dws:EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU", '
                            b'"publicKeyJwk": {"kid": "DHfhTX8nqUdiU2yw5gnx3dFguwAPiR0SzK4I9ugjRoRF", "kty": "OKP", "crv": "Ed25519", "x": "d-FNfyepR2JTbLDmCfHd0WC7AA-JHRLMrgj26CNGhEU"}}], '
                        b'"service": [], '
                        b'"alsoKnownAs": []}, '
                    b'"didResolutionMetadata": {"contentType": "application/did+json", "retrieved": "2025-07-24T19:35:23Z"}, '
                    b'"didDocumentMetadata": {"witnesses": [], "versionId": "2", "equivalentId": []}}'
                )
                # fmt: on
            elif url == keri_cesr_url:
                # whitespace added for readability - this is just bytes and the whitespace does not impact the actual content
                return (
                    b'{"v":"KERI10JSON00012b_","t":"icp",'
                    b'"d":"EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"i":"EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"s":"0",'
                    b'"kt":"1","k":["DHfhTX8nqUdiU2yw5gnx3dFguwAPiR0SzK4I9ugjRoRF"],'
                    b'"nt":"1","n":["EDklD8WWC8ks7U-pdxI_hoftybqLVRTj3KJK70jkq6Ha"],'
                    b'"bt":"0","b":[],"c":[],"a":[]}'
                    b'-VAn-AABAAAVeuv7YV_mWaMsye6tH5-G1x58jyJyPJtNePHS3u6vn5UYMlWBFzShMSabVqAtRvW8YW18uEhEGOaZ-cGkcE0J-EAB0AAAAAAAAAAAAAAAAAAAAAAA1AAG2025-07-24T16c27c22d019596p00c00'
                    b'{"v":"KERI10JSON00013a_","t":"ixn",'
                    b'"d":"EHZquNk1-N_KYQJcdXy_jym_YnwlzvdC_6YmGKp6VvIN",'
                    b'"i":"EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"s":"1","p":"EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"a":[{"i":"EK_yp-mT-9YFKVqyUnqAN0CXUd6cxUGeIvem5I0A8TLb","s":"0","d":"EK_yp-mT-9YFKVqyUnqAN0CXUd6cxUGeIvem5I0A8TLb"}]}'
                    b'-VAn-AABAAAfWrHVECbYrHe5hBQnIdgbbwmNPUO4VFsV0HG9zSwmbA-Qc7PqkQCD3IAZ_CnP5RrV2R_MgeYZtFu7PPwdWw0J-EAB0AAAAAAAAAAAAAAAAAAAAAAB1AAG2025-07-24T16c27c22d043008p00c00'
                    b'{"v":"KERI10JSON00013a_","t":"ixn",'
                    b'"d":"EEy7aFHQPBagfqW4MatcUVRVN7yJfft-3RhTzgZvN3Pf",'
                    b'"i":"EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"s":"2","p":"EHZquNk1-N_KYQJcdXy_jym_YnwlzvdC_6YmGKp6VvIN",'
                    b'"a":[{"i":"EAKC8atqn7nuqB7Iqv_FohuGJz6l3ZhWsISbkQFD522D","s":"0","d":"EHFeHZKRISML75268kN2XvkFueHu-mXj3YZAWU8aQxQQ"}]}'
                    b'-VAn-AABAADnenNyGDisXGeZdQCLSzXl9QoYgBxi7cdYw3baY5ukUonbnIQnUBFBsCqPVvrp_dNibpTPVOWtJSDYNglDTKIH-EAB0AAAAAAAAAAAAAAAAAAAAAAC1AAG2025-07-24T16c53c32d268075p00c00'
                    b'{"v":"KERI10JSON0000ff_","t":"vcp",'
                    b'"d":"EK_yp-mT-9YFKVqyUnqAN0CXUd6cxUGeIvem5I0A8TLb",'
                    b'"i":"EK_yp-mT-9YFKVqyUnqAN0CXUd6cxUGeIvem5I0A8TLb",'
                    b'"ii":"EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"s":"0","c":["NB"],"bt":"0","b":[],"n":"0AC-D5XhLUkO-ODnrJMSRPqv"}'
                    b'-VAS-GAB0AAAAAAAAAAAAAAAAAAAAAABEHZquNk1-N_KYQJcdXy_jym_YnwlzvdC_6YmGKp6VvIN'
                    b'{"v":"KERI10JSON0000ed_","t":"iss",'
                    b'"d":"EHFeHZKRISML75268kN2XvkFueHu-mXj3YZAWU8aQxQQ",'
                    b'"i":"EAKC8atqn7nuqB7Iqv_FohuGJz6l3ZhWsISbkQFD522D",'
                    b'"s":"0","ri":"EK_yp-mT-9YFKVqyUnqAN0CXUd6cxUGeIvem5I0A8TLb","dt":"2025-07-24T16:21:40.802473+00:00"}'
                    b'-VAS-GAB0AAAAAAAAAAAAAAAAAAAAAACEEy7aFHQPBagfqW4MatcUVRVN7yJfft-3RhTzgZvN3Pf'
                    b'{"v":"ACDC10JSON0005f4_",'
                    b'"d":"EAKC8atqn7nuqB7Iqv_FohuGJz6l3ZhWsISbkQFD522D",'
                    b'"i":"EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"ri":"EK_yp-mT-9YFKVqyUnqAN0CXUd6cxUGeIvem5I0A8TLb",'
                    b'"s":"EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5",'
                    b'"a":{'
                    b'"d":"EP75lC-MDk8br72V7r5hxY1S7E7U4pgnsGX2WmGyLPxs",'
                    b'"dt":"2025-07-24T16:21:40.802473+00:00",'
                    b'"ids":['
                    b'"did:web:127.0.0.1%3a7677:dws:EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"did:webs:127.0.0.17677%3a7677:dws:EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"did:web:example.com:EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"did:web:foo.com:EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU",'
                    b'"did:webs:foo.comNone:EMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU"]},'
                    b'"r":{'
                    b'"d":"EEVTx0jLLZDQq8a5bXrXgVP0JDP7j8iDym9Avfo8luLw",'
                    b'"aliasDesignation":{"l":"The issuer of this ACDC designates the identifiers in the ids field as the only allowed namespaced aliases of the issuer\'s AID."},'
                    b'"usageDisclaimer":{"l":"This attestation only asserts designated aliases of the controller of the AID, that the AID controlled namespaced alias has been designated by the controller. It does not assert that the controller of this AID has control over the infrastructure or anything else related to the namespace other than the included AID."},'
                    b'"issuanceDisclaimer":{"l":"All information in a valid and non-revoked alias designation assertion is accurate as of the date specified."},'
                    b'"termsOfUse":{"l":"Designated aliases of the AID must only be used in a manner consistent with the expressed intent of the AID controller."}}}'
                    b'-VA0-FABEMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU0AAAAAAAAAAAAAAAAAAAAAAAEMkO5tGOSTSGY13mdljkFaSuUWBpvGMbdYTGV_7LAXhU-AABAAC29a0oQ7ML0dKq_MNsEUElt7d49KH2-folu9qiHztbLbtHfAU5O1X99TbnExPncL8uW2_mVD9ChYk5fZOK-eMO'
                )
            else:
                raise ValueError(f'Unexpected URL: {url}')

        app = resolving.falcon_app()
        oobiery = oobiing.Oobiery(hby=hby)
        resolver_end = resolving.UniversalResolverResource(hby=hby, oobiery=oobiery, load_url=mock_load_url)
        app.add_route('/1.0/identifiers/{did}', resolver_end)
        client = testing.TestClient(app=app)

        encoded_did_webs = urllib.parse.quote(
            did_webs_did
        )  # to simulate what HIO does to the DID with urllib.parse.quote in Server.buildEnviron

        # Verify did:webs DID doc
        did_webs_response = client.simulate_get(f'/1.0/identifiers/{encoded_did_webs}')

        assert did_webs_response.content_type == 'application/did+ld+json', 'Content-Type should be application/did+ld+json'
        response_diddoc = json.loads(did_webs_response.content)[didding.DD_FIELD]
        did_webs_diddoc = did_webs_diddoc[didding.DD_FIELD]
        assert response_diddoc == did_webs_diddoc, 'did:webs response did document does not match expected diddoc'

        # Verify did:keri DID doc
        encoded_did_keri = urllib.parse.quote(
            did_keri_did
        )  # to simulate what HIO does to the DID with urllib.parse.quote in Server.buildEnviron
        did_keri_response = client.simulate_get(f'/1.0/identifiers/{encoded_did_keri}')

        assert did_keri_response.content_type == 'application/did+ld+json', 'Content-Type should be application/did+ld+json'
        response_diddoc = json.loads(did_keri_response.content)
        did_keri_diddoc = didding.generate_did_doc(hby, did=did_keri_did, aid=aid, oobi=None, meta=False)
        assert response_diddoc == did_keri_diddoc, 'did:keri response did document does not match expected diddoc'

