#
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2016, fokin.denis@gmail.com
# Copyright (c) 2018, Matthias Urlichs
#

"""Asynchronous Swagger client library.
   rewritten with use of anyio libs
"""

import json
import logging
import os.path
import re
import urllib
import asyncswagger11

from asyncswagger11.http_client import AsynchronousHttpClient
from asyncswagger11.processors import WebsocketProcessor, SwaggerProcessor

log = logging.getLogger(__name__)


class ClientProcessor(SwaggerProcessor):
    """Enriches swagger models for client processing.
    """

    def process_resource_listing_api(self, resources, listing_api, context):
        """Add name to listing_api.

        :param resources: Resource listing object
        :param listing_api: ResourceApi object.
        :type context: ParsingContext
        :param context: Current context in the API.
        """
        name, ext = os.path.splitext(os.path.basename(listing_api['path']))
        listing_api['name'] = name

class Operation(object):
    """async Operation object.
    """

    def __init__(self, uri, operation, http_client):
        self.uri = uri
        self.json = operation
        self.http_client = http_client

    def __repr__(self):
        try:
            return "%s(%s)" % (self.__class__.__name__, self.json['nickname'])
        except Exception:
            return "%s(?)" % (self.__class__.__name__,)

    async def __call__(self, **kwargs):
        """Invoke ARI operation.

        :param kwargs: ARI operation arguments.
        :return: Implementation specific response or WebSocket connection
        """
        log.debug("%s?%r" % (self.json['nickname'], urllib.parse.urlencode(kwargs)))
        method = self.json['httpMethod']
        uri = self.uri
        params = {}
        data = None
        headers = {"Accept": "application/json"}
        for param in self.json.get('parameters', []):
            pname = param['name']
            value = kwargs.get(pname)
            # Turn list params into comma separated values
            if isinstance(value, list):
                value = ",".join(value)

            if value is not None:
                if param['paramType'] == 'path':
                    uri = uri.replace('{%s}' % pname,
                                      urllib.parse.quote_plus(str(value)))
                elif param['paramType'] == 'query':
                    params[pname] = value
                elif param['paramType'] == 'body':
                    if not data:
                        data = {}
                    data[pname] = value
                else:
                    raise AssertionError(
                        "Unsupported paramType %s" %
                        param['paramType'])
                del kwargs[pname]
            else:
                if param['required']:
                    raise TypeError(
                        "Missing required parameter '%s' for '%s'" %
                        (pname, self.json['nickname']))
        if kwargs:
            raise TypeError("'%s' does not have parameters %r" %
                            (self.json['nickname'], kwargs.keys()))

        log.debug("%s %s(%r)", method, uri, params)

        if data:
            data = json.dumps(data)
            headers['Content-type'] = 'application/json'

        if self.json['is_websocket']:
            # Fix up http: URLs
            uri = re.sub('^http', "ws", uri)
            if data:
                raise NotImplementedError(
                    "Sending body data with websockets not implmented")
            headers = list(headers.items())
            ret = await self.http_client.ws_connect(uri, params=params,
                    headers=headers)
        else:
            ret = await self.http_client.request(
                method, uri, params=params, headers=headers, data=data)
        return ret


class Resource(object):
    """Swagger resource, described in an API declaration.

    :param resource: Resource model
    :param http_client: HTTP client API
    """

    def __init__(self, resource, http_client):
        # log.debug("Building resource '%s'" % resource['name'])
        self.json = resource
        decl = resource['api_declaration']
        self.http_client = http_client
        self.operations = {
            oper['nickname']: self._build_operation(decl, api, oper)
            for api in decl['apis']
            for oper in api['operations']}

    def __repr__(self):
        try:
            return "%s(%s)" % (self.__class__.__name__, self.json['name'])
        except Exception:
            return "%s(?)" % (self.__class__.__name__,)

    def __getattr__(self, item):
        """Promote operations to be object fields.

        :param item: Name of the attribute to get.
        :rtype: Resource
        :return: Resource object.
        """
        op = self.get_operation(item)
        if not op:
            raise AttributeError("Resource '%s' has no operation '%s'" %
                                 (self.get_name(), item))
        return op

    def get_operation(self, name):
        """Gets the operation with the given nickname.

        :param name: Nickname of the operation.
        :rtype:  Operation
        :return: Operation, or None if not found.
        """
        return self.operations.get(name)

    def get_name(self):
        """Returns the name of this resource.

        Name is derived from the filename of the API declaration.

        :return: Resource name.
        """
        return self.json.get('name')

    def _build_operation(self, decl, api, operation):
        """Build an asynchronous operation object

        :param decl: API declaration.
        :param api: API entry.
        :param operation: Operation.
        """
        # log.debug("Building operation %s.%s" % (
        #   self.get_name(), operation['nickname']))
        uri = decl['basePath'] + api['path']
        return Operation(uri, operation, self.http_client)

class SwaggerClient(object):
    """Client object for accessing a Swagger-documented RESTful service.

    :param url_or_resource: Either the parsed resource listing+API decls, or
                            its URL.
    :type url_or_resource: dict or str
    :param http_client: HTTP client API
    :type  http_client: HttpClient
    """

    def __init__(self, url=None, username='', password='', http_client=None):
        if not http_client:
            http_client = AsynchronousHttpClient(username, password)
        self.http_client = http_client
        self.url = url
        self.loader = asyncswagger11.Loader(
            self.http_client, [WebsocketProcessor(), ClientProcessor()])

    async def init(self):
        if isinstance(self.url, str):
            log.debug("Loading from %s" % self.url)
            self.api_docs = await self.loader.load_resource_listing(self.url)
        else:
            log.debug("Loading from %s" % self.url.get('basePath'))
            self.api_docs = self.url
            self.loader.process_resource_listing(self.api_docs)
        self.resources = {
            resource['name']: Resource(resource, self.http_client)
            for resource in self.api_docs['apis']}

    def __repr__(self):
        try:
            return "%s(%s)" % (self.__class__.__name__, self.api_docs['basePath'])
        except Exception:
            return "%s(?)" % (self.__class__.__name__,)

    def __getattr__(self, item):
        """Promote resource objects to be client fields.

        :param item: Name of the attribute to get.
        :return: Resource object.
        """
        resource = self.get_resource(item)
        if not resource:
            raise AttributeError("API has no resource '%s'" % item)
        return resource

    async def close(self):
        """Close the SwaggerClient, and underlying resources.
        """
        await self.http_client.close()

    def get_resource(self, name):
        """Gets a Swagger resource by name.

        :param name: Name of the resource to get
        :rtype: Resource
        :return: Resource, or None if not found.
        """
        return self.resources.get(name)
