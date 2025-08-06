import datetime
import urllib.parse
from typing import List, Optional, Tuple

import requests
from hio.base import doing
from hio.core import http
from keri.help import helping

from dkr import ArtifactResolveError, log_name, ogler

logger = ogler.getLogger(log_name)


def load_url_with_requests(url: str, timeout: float = 5.0) -> bytes:
    https_url = url[:]
    if not https_url.startswith('https://'):
        https_url = 'https://' + https_url.lstrip('http://')
    response = None
    try:
        response = requests.get(url=https_url, timeout=timeout)
    except requests.exceptions.ConnectionError as e:
        logger.error(f'Failed to connect to HTTPS URL {https_url}: {e}')
    except Exception as e:
        logger.error(f'Failed to load HTTPS URL {https_url}: {e}')
    # Ensure the request was successful
    if response is not None:
        if response.status_code == 200:
            return response.content if response.content else b''
    logger.error(f'Failed to load URL {url}, trying with HTTP')

    http_url = url[:]
    http_url = http_url.replace('https://', 'http://', 1)  # Try with HTTP if HTTPS fails
    try:
        response = requests.get(http_url, timeout=timeout)
    except requests.exceptions.ConnectionError as e:
        logger.error(f'Failed to connect to HTTP URL {http_url}: {e}')
        raise ArtifactResolveError(f'Failed to connect to HTTP URL {http_url}') from e
    except Exception as e:
        logger.error(f'Failed to load HTTP URL {http_url}: {e}')
        raise ArtifactResolveError(f'Failed to load HTTP URL {http_url}') from e
    return response.content if response.status_code == 200 else b''


def load_url_with_hio(url: str, timeout: float = 5.0, method: str = 'GET') -> bytes:
    """Load a URL using the HIO HTTP client, respecting timeout and method."""
    return http_request(method=method, url=url, timeout=timeout)


def create_http_client(method, url, body=None, headers=None) -> (http.clienting.Client, http.ClientDoer):
    """
    Builder function to create an HIO HTTP client and associated ClientDoer for an HTTP request.
    Does not execute the HTTP request.

    Returns:
        Tuple of (http.clienting.Client, ClientDoer) where:
            - http.clienting.Client: The HTTP client configured with the request.
            - ClientDoer: The doer that will be run by a HIO Doist to execute the request.
    """
    parsed_url = urllib.parse.urlparse(url)
    try:
        client = http.clienting.Client(
            scheme=parsed_url.scheme, hostname=parsed_url.hostname, port=parsed_url.port, portOptional=True
        )
    except Exception as e:
        print(f'Error establishing client connection: {e}')
        raise
    if hasattr(body, 'encode'):
        body = body.encode('utf-8')
    client.request(method=method, path=f'{parsed_url.path}?{parsed_url.query}', qargs=None, headers=headers, body=body)
    client_doer = http.clienting.ClientDoer(client=client)
    return client, client_doer


def http_request(
    method: str, url: str, body: Optional[bytes] = None, headers: Optional[dict] = None, timeout: float = 0.0
) -> bytes:
    """Executes an HTTP request using the HIO Doist to run the ClientDoer and return the response body as bytes."""
    client, client_doer = create_http_client(method=method, url=url, body=body, headers=headers)
    doist = doing.Doist(limit=1.0, tock=0.03125, real=True)
    client_deeds = doist.enter([client_doer])
    dt = helping.nowUTC()
    while client.responses is None or len(client.responses) == 0:
        now = helping.nowUTC()
        if (now - dt) > datetime.timedelta(seconds=timeout):
            break
        doist.recur(deeds=client_deeds)
    if len(client.responses) != 0:
        rep = client.respond()
        return bytes(rep.body)
    else:
        raise ArtifactResolveError(f'Failed to load URL {url}, no responses received')


def load_url_with_hio_clienter(url: str, timeout: float = 5.0, method: str = 'GET') -> bytes:
    """Load a URL using the HIO HTTP client"""
    tock = 0.03125
    doist = doing.Doist(
        limit=timeout + tock * 10, tock=0.03125, real=True
    )  # makes Doist run just a bit longer than the HTTP client timeout
    clienter = HTTPClienter(timeout=timeout)
    clienter.always = False
    clienter.tymth = doist.tymen()  # share the Doist tymth with the Clienter
    client = clienter.request(method, url)
    doist.do(doers=[clienter])

    if len(client.responses) != 0:
        rep = client.respond()
        return bytes(rep.body)
    else:
        raise ArtifactResolveError(f'Failed to load URL {url}, no responses received')


class HTTPClienter(doing.DoDoer):
    """
    A DoDoer that manages HIO HTTP clients and their associated ClientDoers for making HTTP requests.
    Supports running multiple clients concurrently and waits for their responses using a HTTPClientMonitor.
    """

    def __init__(self, tymth=None, timeout: float = 5.0):
        """
        Parameters:
            tymth: Tymth instance for time management. If None, uses the default DoDoer's tymth.
            timeout: Timeout in seconds for each HTTP client request.

        Attributes:
            clients: List of tuples containing (http.clienting.Client, ClientDoer, datetime) for each client.
            always: If False, shut down the Clienter when no clients remain. If true, run indefinitely.
            tymth: Tymth instance for time management.
            doers: List of Doers to manage the HTTP clients.
        """
        self.clients: List[(http.clienting.Client, http.ClientDoer, datetime)] = []
        self.always = False
        self.tymth = tymth
        client_worker = HTTPClientMonitor(clients=self.clients, clienter=self, timeout=timeout)
        self.doers = [client_worker]
        super(HTTPClienter, self).__init__(doers=self.doers)

    def request(self, method, url, body=None, headers=None) -> http.clienting.Client | None:
        """
        Creates an HTTP client and its ClientDoer, adding each to the list of clients and
        DoDoer's doers and deeds. The HTTPClientMonitor will remove the client and doer once either
        a response is received or the client times out.

        Returns:
            http.clienting.Client: The HTTP client configured with the request so the caller can access the response.
            None: If an error occurs while establishing the client connection.
        """
        parsed_url = urllib.parse.urlparse(url)
        try:
            client = http.clienting.Client(
                scheme=parsed_url.scheme, hostname=parsed_url.hostname, port=parsed_url.port, portOptional=True
            )
        except Exception as e:
            print(f'Error establishing client connection: {e}')
            raise
        if hasattr(body, 'encode'):
            body = body.encode('utf-8')
        client.request(method=method, path=f'{parsed_url.path}?{parsed_url.query}', qargs=None, headers=headers, body=body)
        client_doer = http.clienting.ClientDoer(client=client)
        self.clients.append((client, client_doer, helping.nowUTC()))
        self.extend([client_doer])  # Add the client doer to the DoDoer's doers list
        return client


class HTTPClientMonitor(doing.Doer):
    """
    Manages a list of HIO HTTP Clients and runs their associated ClientDoers until completion.
    Updates the parent HTTPClienter to remove clients and their doers on request completion or timeout.
    Exits once all clients have a response or time out.
    """

    TimeoutClient = 10.0  # seconds

    def __init__(
        self,
        clients: List[Tuple[http.clienting.Client, http.ClientDoer, datetime]],
        clienter: HTTPClienter,
        timeout: float = 5.0,
        tock=0.0,
    ):
        """
        Parameters:
            clients: List of tuples containing (http.clienting.Client, http.ClientDoer, datetime) for each client.
            clienter: The parent HTTPClienter that manages the clients and their doers.
            tock: Time interval for yielding control in the Doer loop.
        """
        self.clients = clients
        self.clienter: HTTPClienter = clienter
        self.TimeoutClient = timeout
        super(HTTPClientMonitor, self).__init__(tock=tock)

    def wait_on_responses(self):
        """
        Periodically check for responses from clients and remove any that have timed out or received a response.
        Prunes the clients from the parent Clienter client list and the ClientDoers from the parent DoDoer's doers and deeds.
        """
        while len(self.clients) > 0:
            to_remove = []
            for client, doer, dt in self.clients:
                now = helping.nowUTC()
                if (now - dt) > datetime.timedelta(seconds=self.TimeoutClient):  # Timeout check
                    to_remove.append(
                        (client, doer, dt)
                    )  # remove client if it has not received a response in the timeout period
                if client.responses:  # a response has been received so close down its Doer
                    to_remove.append((client, doer, dt))
                yield self.tock  # yielding the tock is necessary to allow precise time control for this Doer.

            for client, doer, dt in to_remove:
                self.clients.remove((client, doer, dt))  # allows this Doer to eventually exit
                self.clienter.remove([doer])  # removes the ClientDoer from the DoDoer's doers and deeds

            yield self.tock  # yielding the tock is necessary to allow precise time control for this Doer.

    def recur(self, tyme=None, tock=0.0):
        """Delegates to wait_on_responses to wait on HTTP client responses and then ends the Doer by returning True."""
        # yield from causes Hio to run this .recur as a generator in Doer.do()
        yield from self.wait_on_responses()
        return True  # indicates Doer is complete and may be removed from DoDoer's doers and deeds
