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
import aiohttp

log = logging.getLogger(__name__)


class HttpClient(object):
    """Interface for a minimal HTTP client.
    """

    def close(self):
        """Close this client resource.
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

    def ws_connect(self, url, params=None):
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

    def apply(self, request):
        """Apply authentication to a request.

        :param request: Request to add authentication information to.
        """
        raise NotImplementedError("%s: Method not implemented",
                                  self.__class__.__name__)

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

    def apply(self, request):
        request.params[self.param_name] = self.api_key


# noinspection PyDocstring
class AsynchronousHttpClient(HttpClient):
    """Asynchronous HTTP client implementation.
    """

    def __init__(self, username, password, loop):
        self.authenticator = aiohttp.BasicAuth(username, password)
        self.websockets = set()
        self.session = aiohttp.ClientSession(loop=loop, auth=self.authenticator)

    async def close(self):
        for websocket in self.websockets:
            await websocket.close()
        await self.session.close()

    async def request(self, method, url, params=None, data=None, headers=None):
        """Requests based implementation.
        :return: aiohttp response
        :rtype:  aiohttp.ClientResponse
        """
        response = await self.session.request(
            method=method, url=url, params=params, data=data, headers=headers)
        return response

    async def ws_connect(self, url, params=None):
        """Websocket-client based implementation.
        :return: aiohttp WebSocket response
        :rtype:  aiohttp.ClientWebSocketResponse
        """
        if params:
            joined_params = "&".join(["%s=%s" % (k, v)
                                     for (k, v) in params.items()])
            url += "?%s" % joined_params
        ret = await self.session.ws_connect(url)
        self.websockets.add(ret)
        return ret
