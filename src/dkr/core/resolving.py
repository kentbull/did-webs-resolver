# -*- encoding: utf-8 -*-
"""
dkr.core.serving module

"""

import json
import os
import queue
import sys
import urllib.parse

import falcon
import requests
from hio.base import doing
from hio.core import http
from keri.app import habbing

from dkr import log_name, ogler
from dkr.core import didding, ends

logger = ogler.getLogger(log_name)


def getSources(did: str, resq: queue.Queue = None):
    logger.info(f'Parsing DID {did}')
    domain, port, path, aid = didding.parseDIDWebs(did=did)

    opt_port = f':{port}' if port is not None else ''
    opt_path = f'/{path.replace(":", "/")}' if path is not None else ''
    base_url = f'http://{domain}{opt_port}{opt_path}/{aid}'

    # Load the did doc
    dd_url = f'{base_url}/{ends.DID_JSON}'
    logger.info(f'Loading DID Doc from {dd_url}')
    dd_res = loadUrl(dd_url, resq=resq)
    logger.info(f'Got DID doc: {dd_res.content.decode("utf-8")}')

    # Load the KERI CESR
    kc_url = f'{base_url}/{ends.KERI_CESR}'
    logger.info(f'Loading KERI CESR from {kc_url}')
    kc_res = loadUrl(kc_url, resq=resq)
    logger.info(f'Got KERI CESR: {kc_res.content.decode("utf-8")}')

    if resq is not None:
        resq.put(aid)
        resq.put(dd_res)
        resq.put(kc_res)
    return aid, dd_res, kc_res


def saveCesr(hby: habbing.Habery, kc_res: requests.Response, aid: str = None):
    logger.info('Saving KERI CESR to hby', kc_res.content.decode('utf-8'))
    hby.psr.parse(ims=bytearray(kc_res.content))
    if aid:
        assert aid in hby.kevers, f'KERI CESR parsing failed, KERI AID {aid} not found in habery'


def getComp(hby: habbing.Habery, did: str, aid: str, dd_res: requests.Response, kc_res: requests.Response):
    dd = didding.generateDIDDoc(hby, did=did, aid=aid, oobi=None, meta=True)
    dd[didding.DD_META_FIELD]['didDocUrl'] = dd_res.url
    dd[didding.DD_META_FIELD]['keriCesrUrl'] = kc_res.url

    dd_actual = didding.fromDidWeb(json.loads(dd_res.content.decode('utf-8')))
    logger.info(f'Got DID Doc: {dd_actual}')

    return dd, dd_actual


def verify(dd, dd_actual, meta: bool = False):
    dd_exp = dd
    if didding.DD_FIELD in dd_exp:
        dd_exp = dd[didding.DD_FIELD]
    # TODO verify more than verificationMethod
    verified = _verifyDidDocs(dd_exp[didding.VMETH_FIELD], dd_actual[didding.VMETH_FIELD])

    result = None
    if verified:
        result = dd if meta else dd[didding.DD_FIELD]
        logger.info(f'DID verified')
    else:
        didresult = dict()
        didresult[didding.DD_FIELD] = None
        if didding.DID_RES_META_FIELD not in didresult:
            didresult[didding.DID_RES_META_FIELD] = dict()
        didresult[didding.DID_RES_META_FIELD]['error'] = 'notVerified'
        didresult[didding.DID_RES_META_FIELD]['errorMessage'] = (
            'The DID document could not be verified against the KERI event stream'
        )
        result = didresult
        logger.info(f'DID verification failed')

    return result


def _verifyDidDocs(expected, actual):
    # TODO determine what to do with BADA RUN things like services (witnesses) etc.
    if expected != actual:
        logger.info('DID Doc does not verify', file=sys.stderr)
        _compare_dicts(expected, actual)
        return False
    else:
        logger.info('DID Doc verified', file=sys.stderr)
        return True


def _compare_dicts(expected, actual, path=''):
    logger.info(f'Comparing dictionaries:\nexpected:\n{expected}\n \nand\n \nactual:\n{actual}', file=sys.stderr)

    """Recursively compare two dictionaries and print differences."""
    if isinstance(expected, dict):
        for k in expected.keys():
            # Construct current path
            current_path = f'{path}.{k}' if path else k
            logger.info(f'Comparing key {current_path}', file=sys.stderr)

            # Key not present in the actual dictionary
            if k not in actual:
                logger.info(f'Key {current_path} not found in the actual dictionary', file=sys.stderr)
                continue

            # If value in expected is a dictionary but not in actual
            if isinstance(expected[k], dict) and not isinstance(actual[k], dict):
                logger.info(f'{current_path} is a dictionary in expected, but not in actual', file=sys.stderr)
                continue

            # If value in actual is a dictionary but not in expected
            if isinstance(actual[k], dict) and not isinstance(expected[k], dict):
                logger.info(f'{current_path} is a dictionary in actual, but not in expected', file=sys.stderr)
                continue

            # If value is another dictionary, recurse
            if isinstance(expected[k], dict) and isinstance(actual[k], dict):
                _compare_dicts(expected[k], actual[k], current_path)
            # Compare non-dict values
            elif expected[k] != actual[k]:
                logger.info(
                    f'Different values for key {current_path}: {expected[k]} (expected) vs. {actual[k]} (actual)',
                    file=sys.stderr,
                )

        if isinstance(actual, dict):
            # Check for keys in actual that are not present in expected
            for k in actual.keys():
                current_path = f'{path}.{k}' if path else k
                if k not in expected:
                    logger.info(f'Key {current_path} not found in the expected dictionary', file=sys.stderr)
        else:
            logger.info(f'Expecting actual did document to contain dictionary {expected}', file=sys.stderr)
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            logger.info(f'Expected list {expected} and actual list {actual} are not the same length', file=sys.stderr)
        else:
            for i in range(len(expected)):
                _compare_dicts(expected[i], actual[i], path)
    else:
        if expected != actual:
            logger.info(f'Different values for key {path}: {expected} (expected) vs. {actual} (actual)', file=sys.stderr)


def resolve(hby, did, meta=False, resq: queue.Queue = None):
    """Resolve a did:webs DID and returl the verification result."""
    aid, dd_res, kc_res = getSources(did=did, resq=resq)
    saveCesr(hby=hby, kc_res=kc_res, aid=aid)
    dd, dd_actual = getComp(hby=hby, did=did, aid=aid, dd_res=dd_res, kc_res=kc_res)
    vresult = verify(dd, dd_actual, meta=meta)
    logger.info('Resolution result: ', vresult)
    return vresult


# # Test with the provided dictionaries
# expected_dict = {
#     'id': 'did:webs:127.0.0.1%3a7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha',
#     'verificationMethod': [{'id': 'did:webs:127.0.0.1%3a7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha#key-0', 'type': 'Ed25519VerificationKey2020', 'controller': 'did:webs:127.0.0.1%3a7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha', 'publicKeyMultibase': 'z2fD7Rmbbggzwa4SNpYKWi6csiiUcVeyUTgGzDtMrqC7b'}]
# }

# actual_dict = {
#     "id": "did:webs:127.0.0.1%3a7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
#     "verificationMethod": [{
#         "id": "did:webs:127.0.0.1%3a7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha#key-0",
#         "type": "Ed25519VerificationKey2020",
#         "controller": "did:webs:127.0.0.1%3a7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
#         "publicKeyMultibase": "z2fD7Rmbbggzwa4SNpYKWi6csiiUcVeyUTgGzDtMrqC7b"
#     }]
# }

# compare_dicts(expected_dict, actual_dict)


def setup(hby, hbyDoer, oobiery, *, httpPort, cf=None, staticFilesDir='dws'):
    """Setup serving package and endpoints

    Parameters:
        hby (Habery): identifier database environment
        hbyDoer (HaberyDoer): Doer for the identifier database environment
        oobiery (Oobiery): OOBI management environment
        httpPort (int): external port to listen on for HTTP messages
    Returns:
        list: list of Doers to run in the Tymist
    """
    logger.info(f'Setting up Resolver HTTP server Doers on port {httpPort}')
    app = falcon.App(
        middleware=falcon.CORSMiddleware(
            allow_origins='*', allow_credentials='*', expose_headers=['cesr-attachment', 'cesr-date', 'content-type']
        )
    )

    server = http.Server(port=httpPort, app=app)
    httpServerDoer = http.ServerDoer(server=server)

    loadEnds(app, hby=hby, hbyDoer=hbyDoer, oobiery=oobiery, staticFilesDir=staticFilesDir)

    doers = [httpServerDoer]

    return doers


def loadEnds(app, *, hby, hbyDoer, oobiery, staticFilesDir):
    # Set up static file serving for did.json and keri.cesr files
    did_doc_dir = hby.cf.get().get('did.doc.dir', 'dws')
    if not os.path.isabs(did_doc_dir):
        did_doc_dir = os.path.join(os.path.abspath(staticFilesDir), did_doc_dir)
    if not os.path.isabs(did_doc_dir):
        did_doc_dir = os.path.join(os.getcwd(), did_doc_dir)
    logger.info(f'Serving static files from {did_doc_dir}')
    app.add_static_route('/dws', did_doc_dir)

    resolveEnd = ResolveResource(hby=hby, hbyDoer=hbyDoer, oobiery=oobiery)
    app.add_route('/1.0/identifiers/{did}', resolveEnd)
    return [resolveEnd]


class ResolveResource(doing.DoDoer):
    """
    Resource for managing OOBIs

    """

    def __init__(self, hby, hbyDoer, oobiery):
        """Create Endpoints for discovery and resolution of OOBIs

        Parameters:
            hby (Habery): identifier database environment

        """
        self.hby = hby
        self.hbyDoer = hbyDoer
        self.oobiery = oobiery

        super(ResolveResource, self).__init__(doers=[])

    def on_get(self, req, rep, did, meta=False):
        """
        Handle GET requests to resolve a DID by its identifier (KERI AID).

        Parameters:
            req (falcon.Request): The HTTP request object.
            rep (falcon.Response): The HTTP response object.
            did (str): The DID to resolve.
            meta (bool): If True, include metadata in the DID document resolution.
        """
        # did = urllib.parse.unquote(did)
        logger.info(f'Request to resolve did: {did}')

        if did is None:
            rep.status = falcon.HTTP_400
            rep.content_type = 'application/json'
            rep.media = {'error': "invalid resolution request body, 'did' is required"}
            return

        if 'oobi' in req.params:
            oobi = req.params['oobi']
            logger.info(f'From parameters {req.params} got oobi: {oobi}')
        else:
            oobi = None

        if did.startswith('did:webs:'):
            # res = WebsResolver(hby=self.hby, hbyDoer=self.hbyDoer, obl=self.obl, did=did)
            # tymth = None # ???
            # data = res.resolve(tymth)
            data = resolve(hby=self.hby, did=did, meta=meta)
        elif did.startswith('did:keri'):
            # res = KeriResolver(hby=self.hby, hbyDoer=self.hbyDoer, obl=self.obl, did=did, oobi=oobi, metadata=False)
            # tymth = None # ???
            # data = res.resolve(tymth)
            cmd = f'dkr did keri resolve --name dkr --did {did} --oobi {oobi} --meta {meta}'
            stream = os.popen(cmd)
            data = stream.read()
        else:
            rep.status = falcon.HTTP_400
            rep.media = {'error': "invalid 'did'"}
            return

        rep.status = falcon.HTTP_200
        rep.set_header('Content-Type', 'application/did+ld+json')
        rep.body = data

        return


def loadFile(file_path):
    # Read the file in binary mode
    with open(file_path, 'rb') as file:
        msgs = file.read()
        return msgs


def loadJsonFile(file_path):
    # Read the file in binary mode
    with open(file_path, 'r', encoding='utf-8') as file:
        msgs = json.load(file)
        return msgs


def loadUrl(url: str, resq: queue.Queue = None):
    response = requests.get(url=url)
    # Ensure the request was successful
    response.raise_for_status()
    # Convert the content to a bytearray
    if resq is not None:
        resq.put(response)
    return response


def splitCesr(s, char):
    # Find the last occurrence of the character
    index = s.rfind(char)

    # If the character is not found, return the whole string and an empty string
    if index == -1:
        return s, ''

    json_str = s[: index + 1]
    # quote escaped starts with single quote and double quote and the split will lose the closing single/double quote
    if json_str.startswith('"'):
        json_str = json_str + '"'

    cesr_sig = s[index + 1 :]
    if cesr_sig.endswith('"'):
        cesr_sig = '"' + json_str

    # Split the string into two parts
    return json_str, cesr_sig
