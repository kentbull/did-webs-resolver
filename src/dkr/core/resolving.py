# -*- encoding: utf-8 -*-
"""
dkr.core.serving module

"""

import json
import os
import urllib.parse

import falcon
import requests
from hio.base import doing
from hio.core import http, tcp
from keri import kering
from keri.app import habbing
from keri.app.habbing import Habery, HaberyDoer
from keri.app.oobiing import Oobiery

from dkr import log_name, ogler
from dkr.core import didding, ends

logger = ogler.getLogger(log_name)


def load_file(file_path):
    # Read the file in binary mode
    with open(file_path, 'rb') as file:
        msgs = file.read()
        return msgs


def load_json_file(file_path):
    # Read the file in binary mode
    with open(file_path, 'r', encoding='utf-8') as file:
        msgs = json.load(file)
        return msgs


def load_url(url: str):
    try:
        response = requests.get(url=url)
    except requests.exceptions.ConnectionError as e:
        logger.error(f'Failed to connect to URL {url}: {e}')
        raise
    # Ensure the request was successful
    response.raise_for_status()
    return response


def split_cesr(s, char):
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


def get_urls(did: str) -> (str, str, str):
    domain, port, path, aid = didding.parse_did_webs(did=did)

    opt_port = f':{port}' if port is not None else ''
    opt_path = f'/{path.replace(":", "/")}' if path is not None else ''
    base_url = f'http://{domain}{opt_port}{opt_path}/{aid}'

    # did.json for DID Document
    dd_url = f'{base_url}/{ends.DID_JSON}'

    # keri.cesr for CESR stream
    kc_url = f'{base_url}/{ends.KERI_CESR}'
    return aid, dd_url, kc_url


def get_did_artifacts(did: str) -> (str, requests.Response, requests.Response):
    aid, dd_url, kc_url = get_urls(did=did)

    # Load the did doc
    logger.info(f'Loading DID Doc from {dd_url}')
    dd_res = load_url(dd_url)
    logger.debug(f'Got DID doc: {dd_res.content.decode("utf-8")}')

    # Load the KERI CESR
    logger.info(f'Loading KERI CESR from {kc_url}')
    kc_res = load_url(kc_url)
    logger.debug(f'Got KERI CESR: {kc_res.content.decode("utf-8")}')

    return aid, dd_res, kc_res


def save_cesr(hby: Habery, kc_res: requests.Response, aid: str = None):
    logger.info('Saving KERI CESR to hby: %s', kc_res.content.decode('utf-8'))
    hby.psr.parse(ims=bytearray(kc_res.content))
    if (
        aid not in hby.kevers
    ):  # After parsing then the AID should be in kevers, meaning the KEL for the AID is locally available
        raise kering.KeriError(f'KERI CESR parsing and saving failed, KERI AID {aid} not found in habery')


def compare_did_docs(
    hby: habbing.Habery, did: str, aid: str, meta: bool, dd_res: requests.Response, kc_res: requests.Response
):
    dd = didding.generate_did_doc(hby, did=did, aid=aid, oobi=None, meta=meta)
    if meta:
        dd[didding.DD_META_FIELD]['didDocUrl'] = dd_res.url
        dd[didding.DD_META_FIELD]['keriCesrUrl'] = kc_res.url

    dd_actual = didding.from_did_web(json.loads(dd_res.content.decode('utf-8')), meta)
    logger.debug(f'Got DID Doc: {dd_actual}')

    return dd, dd_actual


def error_resolution_response(meta: bool, error_message: str):
    """
    Generate an error response for DID resolution.
    """
    didresult = dict()
    didresult[didding.DD_FIELD] = None
    if didding.DID_RES_META_FIELD not in didresult:
        didresult[didding.DID_RES_META_FIELD] = dict()
    didresult[didding.DID_RES_META_FIELD]['error'] = 'notVerified'
    didresult[didding.DID_RES_META_FIELD]['errorMessage'] = error_message
    result = didresult
    return result


def verify(dd_expected: dict, dd_actual: dict, meta: bool = False) -> (bool, dict):
    """
    Verify the DID document against the KERI event stream.

    Returns:
         tuple(bool, dict): (verified, dd) where verified is a boolean indicating verification status
    """
    dd_exp = dd_expected
    if didding.DD_FIELD in dd_exp:
        dd_exp = dd_expected[didding.DD_FIELD]
    # TODO verify more than verificationMethod
    verified = _verify_did_docs(dd_exp[didding.VMETH_FIELD], dd_actual[didding.VMETH_FIELD])

    if verified:
        logger.info(f'DID document verified')
        return (True, dd_expected[didding.DD_FIELD]) if meta else (True, dd_expected)
    else:
        logger.info(f'DID document verification failed')
        return (
            False,
            error_resolution_response(
                meta=meta, error_message='The DID document could not be verified against the KERI event stream'
            ),
        )


def _verify_did_docs(expected, actual):
    # TODO determine what to do with BADA RUN things like services (witnesses) etc.
    if (
        expected != actual
    ):  # Python != and == perform a deep object value comparison; this is not reference equality, it is value equality
        differences = _compare_dicts(expected, actual)
        logger.error(f'Differences found in DID Doc verification: {differences}')
        return False
    else:
        return True


def _compare_dicts(expected, actual, path=''):
    """Recursively compare two dictionaries and return differences."""
    logger.error(f'Comparing dictionaries:\nexpected:\n{expected}\n \nand\n \nactual:\n{actual}')
    differences = []

    if isinstance(expected, dict):
        for k in expected.keys():
            # Construct current path
            current_path = f'{path}.{k}' if path else k
            logger.error(f'Comparing key {current_path}')

            # Key not present in the actual dictionary
            if k not in actual:
                differences.append((current_path, expected[k], None))
                logger.error(f'Key {current_path} not found in the actual dictionary')
                continue

            # If value in expected is a dictionary but not in actual
            if isinstance(expected[k], dict) and not isinstance(actual[k], dict):
                differences.append((current_path, expected[k], actual[k]))
                logger.error(f'{current_path} is a dictionary in expected, but not in actual')
                continue

            # If value in actual is a dictionary but not in expected
            if isinstance(actual[k], dict) and not isinstance(expected[k], dict):
                differences.append((current_path, expected[k], actual[k]))
                logger.error(f'{current_path} is a dictionary in actual, but not in expected')
                continue

            # If value is another dictionary, recurse
            if isinstance(expected[k], dict) and isinstance(actual[k], dict):
                differences.append(_compare_dicts(expected[k], actual[k], current_path))
            # Compare non-dict values
            elif expected[k] != actual[k]:
                differences.append((current_path, expected[k], actual[k]))
                logger.error(f'Different values for key {current_path}: {expected[k]} (expected) vs. {actual[k]} (actual)')

        if isinstance(actual, dict):
            # Check for keys in actual that are not present in expected
            for k in actual.keys():
                current_path = f'{path}.{k}' if path else k
                if k not in expected:
                    differences.append((current_path, None, actual[k]))
                    logger.error(f'Key {current_path} not found in the expected dictionary')
        else:
            differences.append((path, expected, None))
            logger.error(f'Expecting actual did document to contain dictionary {expected}')
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            differences.append((path, expected, actual))
            logger.error(f'Expected list {expected} and actual list {actual} are not the same length')
        else:
            for i in range(len(expected)):
                differences.append(_compare_dicts(expected[i], actual[i], path))
    else:
        if expected != actual:
            differences.append((path, expected, actual))
            logger.error(f'Different values for key {path}: {expected} (expected) vs. {actual} (actual)')
    return differences


def resolve(hby: Habery, did: str, meta: bool = False):
    """Resolve a did:webs DID and returl the verification result."""
    aid, dd_res, kc_res = get_did_artifacts(did=did)
    save_cesr(hby=hby, kc_res=kc_res, aid=aid)
    dd, dd_actual = compare_did_docs(hby=hby, did=did, aid=aid, meta=meta, dd_res=dd_res, kc_res=kc_res)
    return verify(dd, dd_actual, meta=meta)


def falcon_app() -> falcon.App:
    """Create a Falcon app instance with open CORS settings."""
    return falcon.App(
        middleware=falcon.CORSMiddleware(
            allow_origins='*',
            allow_credentials='*',
            expose_headers=[
                'cesr-attachment',
                'cesr-date',
                'content-type',
                'signature',
                'signature-input',
                'signify-resource',
                'signify-timestamp',
            ],
        )
    )


def tls_falcon_server(app: falcon.App, http_port: int, keypath: str, certpath: str, cafilepath: str) -> http.Server:
    """Add TLS support to a Falcon server."""
    if keypath is not None:
        servant = tcp.ServerTls(certify=False, keypath=keypath, certpath=certpath, cafilepath=cafilepath, port=http_port)
    else:
        servant = None

    server = http.Server(port=http_port, app=app, servant=servant)
    return server


def setup_resolver(
    hby, hby_doer, oobiery, http_port, static_files_dir=None, did_path=None, keypath=None, certpath=None, cafilepath=None
):
    """Setup serving package and endpoints

    Parameters:
        hby (Habery): identifier database environment
        hby_doer (HaberyDoer): Doer for the identifier database environment
        oobiery (Oobiery): OOBI management environment
        http_port (int): external port to listen on for HTTP messages
        static_files_dir (str): directory to serve static files from, default is None (disabled)
        did_path (str): path segment of the did:webs URL to host the did:webs artifacts on, disabled if None
        keypath (str): path to the TLS private key file, default is None (disabled)
        certpath (str): path to the TLS certificate file, default is None (disabled)
        cafilepath (str): path to the CA certificate file, default is None (disabled)
    Returns:
        list: list of Doers to run in the Tymist
    """
    logger.info(f'Setting up Resolver HTTP server Doers on port {http_port}')
    app = falcon_app()

    server = tls_falcon_server(app, http_port=http_port, keypath=keypath, certpath=certpath, cafilepath=cafilepath)
    http_server_doer = http.ServerDoer(server=server)

    load_ends(app, hby=hby, hby_doer=hby_doer, oobiery=oobiery, static_files_dir=static_files_dir, did_path=did_path)

    doers = [http_server_doer]

    return doers


def serve_artifacts(app: falcon.App, hby: habbing.Habery, static_files_dir: str | None = None, did_path: str = ''):
    """Set up static file serving for did.json and keri.cesr files"""
    if static_files_dir is not None:
        did_doc_dir = hby.cf.get().get('did.doc.dir', 'dws')
        if not os.path.isabs(did_doc_dir):
            did_doc_dir = os.path.join(os.path.abspath(static_files_dir), did_doc_dir)
        if not os.path.isabs(did_doc_dir):
            did_doc_dir = os.path.join(os.getcwd(), did_doc_dir)
        logger.info(f'Serving static files from {did_doc_dir}')
        # Host did:webs artifacts only if static path specified
        app.add_static_route('' if did_path is None else f'/{did_path}', did_doc_dir)


def load_ends(app, hby, hby_doer, oobiery, static_files_dir, did_path=''):
    """Set up Falcon HTTP server endpoints for resolving DIDs and hosting static files"""
    serve_artifacts(app, hby, static_files_dir, did_path)
    resolve_end = UniversalResolverResource(hby=hby, hby_doer=hby_doer, oobiery=oobiery)
    app.add_route('/1.0/identifiers/{did}', resolve_end)
    app.add_route('/health', ends.HealthEnd())
    return [resolve_end]


class UniversalResolverResource(doing.DoDoer):
    """
    HTTP Resource enabling the Universal Resolver to resolve did:webs and did:keri DIDs using the /v1.0/identifiers/{did} endpoint.
    """

    def __init__(self, hby: Habery, hby_doer: HaberyDoer, oobiery: Oobiery):
        """Create Endpoints for discovery and resolution of OOBIs

        Parameters:
            hby (Habery): identifier database environment
            hby_doer (HaberyDoer): Doer for the identifier database environment
            oobiery (Oobiery): OOBI management environment
        """
        self.hby: Habery = hby
        self.oobiery: Oobiery = oobiery

        super(UniversalResolverResource, self).__init__(doers=[])

    @staticmethod
    def requote(encoded_did: str):
        """
        Due to compliance with PEP3333 in PR 38 to HIO (https://github.com/ioflo/hio/pull/38) the
        WSGI container for the Falcon server URL encodes the URL path which means that  the did:webs and did:keri
        DIDs must be URL decoded, broken apart, and then re-encoded to ensure they are valid for resolution.

        This specific attribute of the WSGI environment uses urllib.parse.quote to encode the path, so we need to decode it
        environ['PATH_INFO'] = quote(requestant.path)
        """
        if encoded_did.lower().startswith('did%3awebs') or encoded_did.lower().startswith('did%3akeri'):
            # The DID is incorrectly fully URL-encoded, happens with some WSGI servers, so must decode and re-encode it
            # this happens in Falcon
            try:
                did = urllib.parse.unquote(encoded_did)
            except Exception as e:
                raise ValueError(f'Invalid DID: {encoded_did}, error: {str(e)}')
            did = didding.re_encode_invalid_did(did)
            return did
        else:
            return encoded_did

    def on_get(self, req: falcon.Request, rep: falcon.Response, did: str, meta: bool = False):
        """
        Handle GET requests to resolve a DID by its identifier (KERI AID).

        Parameters:
            req (falcon.Request): The HTTP request object.
            rep (falcon.Response): The HTTP response object.
            did (str): The DID to resolve.
            meta (bool): If True, include metadata in the DID document resolution.
        """
        if did is None:
            rep.status = falcon.HTTP_400
            rep.content_type = 'application/json'
            rep.media = {'error': "invalid resolution request body, 'did' is required"}
            return

        try:
            did = self.requote(did)  # Re-quote the DID to ensure it is valid for resolution
        except ValueError as e:
            rep.status = falcon.HTTP_400
            rep.content_type = 'application/json'
            rep.media = {'message': f'invalid DID: {did}', 'error': str(e)}
            return
        logger.info(f'Request to resolve did: {did}')

        if 'oobi' in req.params:
            oobi = req.params['oobi']
            logger.info(f'From parameters {req.params} got oobi: {oobi}')
        else:
            oobi = None

        if did.startswith('did:webs'):
            result, data = resolve(hby=self.hby, did=did, meta=meta)
        elif did.startswith('did:keri'):
            # Option 1 - does not support OOBI resolution
            # result, data = resolve_did_keri(self.hby, did, oobi, meta)

            # Option 2 - bad design - shelling out
            result, data = resolve_did_keri_cli(self.hby.name, did, oobi, meta)
        else:
            rep.status = falcon.HTTP_400
            rep.media = {'error': "invalid 'did'"}
            return

        rep.status = falcon.HTTP_200
        # rep.set_header('Content-Type', 'application/did+ld+json')
        rep.set_header('Content-Type', 'application/json')
        rep.media = data
        return


def resolve_did_keri_cli(hby_name: str, did: str, oobi: str = None, meta: bool = False):
    """Shell out to a new process using the CLI to run `dkr did keri resolve"""
    cmd = f'dkr did keri resolve --name {hby_name} --did {did} --verbose'
    if oobi is not None:
        cmd += f'--oobi {oobi} '
    if meta:
        cmd += '--meta '
    pipe = os.popen(cmd)
    output = str(pipe.read()).rstrip()
    status = pipe.close()
    if status is not None:
        exit_code = os.waitstatus_to_exitcode(status)
        if exit_code != 0:
            logger.error(f'Error resolving did:keri DID {did} with OOBI {oobi}: {output}')
            return False, {'error': f'Error resolving did:keri DID {did} with OOBI {oobi}: {output}'}
        else:
            logger.info(f'Successfully resolved did:keri DID {did} with OOBI {oobi}: {output}')
            return True, output
    else:
        logger.info(f"Command '{cmd}' might not have returned an exit code, assuming success")
        return True, output


def resolve_did_keri(hby: Habery, did: str, oobi: str = None, meta: bool = False):
    aid = didding.parse_did_keri(did)
    if oobi is not None and hby.db.roobi.get(keys=(oobi,)) is None:
        False, {'error': f'OOBI {oobi} not found in the Habery'}
    return True, didding.generate_did_doc(hby, did=did, aid=aid, oobi=oobi, meta=meta)
