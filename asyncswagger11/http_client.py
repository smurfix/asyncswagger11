#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2016, fokin.denis@gmail.com
# Copyright (c) 2018, Matthias Urlichs
#

"""HTTP client abstractions.
"""

import logging
import urllib.parse
import asks
import base64
import json
from asyncwebsockets import create_websocket

from http import HTTPStatus

log = logging.getLogger(__name__)

error_map = {}
for k,v in HTTPStatus.__members__.items():
    error_map[v] = k

class HttpClient(object):
    """Interface for a minimal HTTP client.
    """

    def close(self):
        """Close this client resource.
        """
        raise NotImplementedError(
            "%s: Method not implemented", self.__class__.__name__)

    def set_basic_auth(self, host, username, password):
        """Configures client to use HTTP Basic authentication.

        :param host: Hostname to limit authentication to.
        :param username: Username
        :param password: Password
        """
        raise NotImplementedError(
            "%s: Method not implemented", self.__class__.__name__)

    def set_api_key(self, host, api_key, param_name='api_key'):
        """Configures client to use api_key authentication.

        The api_key is added to every query parameter sent.

        :param host: Hostname to limit authentication to.
        :param api_key: Value for api_key.
        :param param_name: Parameter name to use in query string.
        """
        raise NotImplementedError(
            "%s: Method not implemented", self.__class__.__name__)


    def request(self, method, url, params=None, data=None):
        """Issue an HTTP request.

        :param method: HTTP method (GET, POST, DELETE, etc.)
        :type  method: str
        :param url: URL to request
        :type  url: str
        :param params: Query parameters (?key=value)
        :type  params: dict
        :param data: Request body
        :type  data: Dictionary, bytes, or file-like object
        :return: Implementation specific response object
        """
        raise NotImplementedError(
            "%s: Method not implemented", self.__class__.__name__)

    def ws_connect(self, url, params=None, headers=None):
        """Create a WebSocket connection.

        :param url: WebSocket URL.
        :type  url: str
        :param params: Query parameters (?key=value)
        :type  params: dict
        :return: Implmentation specific WebSocket connection object
        """
        raise NotImplementedError(
            "%s: Method not implemented", self.__class__.__name__)


class Authenticator(object):
    """Authenticates requests.

    :param host: Host to authenticate for.
    """

    def __init__(self, host):
        self.host = host

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.host)

    def matches(self, url):
        """Returns true if this authenticator applies to the given url.

        :param url: URL to check.
        :return: True if matches host, port and scheme, False otherwise.
        """
        split = urllib.parse.urlsplit(url)
        return self.host == split.hostname

    def apply(self, headers, params):
        """Apply authentication to a request.

        :param headers: Headers to add authentication information to.
        """
        raise NotImplementedError("%s: Method not implemented",
                                  self.__class__.__name__)

class BasicAuthenticator(Authenticator):
    """HTTP Basic authenticator.

    :param host: Host to authenticate for.
    :param username: Username.
    :param password: Password
    """

    def __init__(self, host, username, password):
        super(BasicAuthenticator, self).__init__(host)
        self.username = username
        self.password = password

    def apply(self, headers, params):
        headers['Authorization'] = "Basic " + \
            base64.b64encode((self.username+':'+self.password).encode("utf-8")).decode("ascii")

# noinspection PyDocstring
class ApiKeyAuthenticator(Authenticator):
    """?api_key authenticator.

    This authenticator adds a query parameter to specify an API key.

    :param host: Host to authenticate for.
    :param api_key: API key.
    :param param_name: Query parameter specifying the API key.
    """

    def __init__(self, host, api_key, param_name='api_key'):
        super(ApiKeyAuthenticator, self).__init__(host)
        self.param_name = param_name
        self.api_key = api_key

    def apply(self, headers, params):
        params[self.param_name] = self.api_key


# noinspection PyDocstring
class AsynchronousHttpClient(HttpClient):
    """Asynchronous HTTP client implementation.
    """

    def __init__(self, username='', password='', auth=None):
        if auth is None:
            if username or password:
                auth = BasicAuthenticator(None, username, password)
        elif username or password:
            raise RuntimeError("Conflicting authentication:"
                " use user+pass or auth, not both")
        self.authenticator = auth
        self.websockets = set()
        self.session = asks.Session(connections=3)

    def set_basic_auth(self, host, username, password):
        self.authenticator = BasicAuthenticator(
            host=host, username=username, password=password)

    def set_api_key(self, host, api_key, param_name='api_key'):
        self.authenticator = ApiKeyAuthenticator(
            host=host, api_key=api_key, param_name=param_name)

    async def close(self):
        for websocket in self.websockets:
            await websocket.close()
        await self.session.close()

    async def request(self, method, url, params=None, data=None, headers=None):
        """Requests based implementation.
        :return: asks response
        :rtype:  asks.Response
        """
        if self.authenticator is not None and \
            self.authenticator.matches(url):
            if params is None:
                params = {}
            if headers is None:
                headers = {}
            self.authenticator.apply(headers, params)

        # The socket might be closed … so just retry.
        try:
            response = await self.session.request(
                method=method, url=url, params=params, data=data, headers=headers)
        except asks.errors.BadHttpResponse:
            await self.session.close()  # this flushes any open connections
            response = await self.session.request(
                method=method, url=url, params=params, data=data, headers=headers)

        if response.status_code >= 400:
            text = response.text
            data = None
            if response.status_code == 400:
                try:
                    data = json.loads(text)
                except Exception:
                    pass
            try:
                response.raise_for_status()
            except Exception as err:
                err.data = data
                raise
        return response

    async def ws_connect(self, url, params=None, headers=None):
        """Websocket-client based implementation.
        :return: asyncwebsockets connection
        :rtype:  asyncwebsockets.ClientWebsocket
        """
        if params is None:
            params = {}
        if self.authenticator is not None and \
            self.authenticator.matches(url):
            self.authenticator.apply(params, params)

        if params:
            joined_params = "&".join(["%s=%s" % (k, v)
                                     for (k, v) in params.items()])
            url += "?%s" % joined_params
        # ret = await self.session.ws_connect(url)
        ret = await create_websocket(url, headers=headers)
        self.websockets.add(ret)
        return ret

