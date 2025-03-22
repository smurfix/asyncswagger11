#!/usr/bin/env python
import base64

import pytest
from mocket.plugins.httpretty import httpretty,async_httprettified

from asyncswagger11.http_client import AsynchronousHttpClient, \
    ApiKeyAuthenticator, BasicAuthenticator


# noinspection PyDocstring
class TestAsynchronousClient:
    @pytest.mark.anyio
    @async_httprettified
    async def test_simple_get(self, client):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py.invalid/client-test",
            body='expected')

        resp = await client.request('GET', "http://swagger.py.invalid/client-test",
                           params={'foo': 'bar'})
        assert resp.status_code == 200
        assert resp.read() == b'expected'
        assert httpretty.last_request.querystring == {'foo': ['bar']}
    test_simple_get.basic_auth = ("swagger.py.invalid", 'unit', 'peekaboo')

    @pytest.mark.anyio
    @async_httprettified
    async def test_real_post(self, client):
        httpretty.register_uri(
            httpretty.POST, "http://swagger.py.invalid/client-test",
            body='expected', content_type='text/json')

        resp = await client.request('POST', "http://swagger.py.invalid/client-test",
                           data={'foo': 'bar'})
        assert resp.status_code == 200
        assert resp.read() == b'expected'
        assert httpretty.last_request.headers['content-type'] == \
                'application/x-www-form-urlencoded'
        assert httpretty.last_request.body == b"foo=bar"

    @pytest.mark.anyio
    @async_httprettified
    async def test_basic_auth(self, client):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py.invalid/client-test",
            body='expected')

        resp = await client.request('GET', "http://swagger.py.invalid/client-test",
                           params={'foo': 'bar'})
        assert resp.status_code == 200
        assert resp.read() == b'expected'
        assert httpretty.last_request.querystring == {'foo': ['bar']}
        assert httpretty.last_request.headers.get('authorization') == \
                'Basic '+ base64.b64encode(b"unit:peekaboo").decode()
    test_basic_auth.auth = BasicAuthenticator(host="swagger.py.invalid",
            username="unit", password='peekaboo')

    @pytest.mark.anyio
    @async_httprettified
    async def test_api_key(self, client):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py.invalid/client-test",
            body='expected')

        resp = await client.request('GET', "http://swagger.py.invalid/client-test",
                           params={'foo': 'bar'})
        assert resp.status_code == 200
        assert resp.read() == b'expected'
        assert httpretty.last_request.querystring == \
                {'foo': ['bar'], 'test': ['abc123']}
    test_api_key.auth = ApiKeyAuthenticator("swagger.py.invalid",
                        'abc123', param_name='test')

    @pytest.mark.anyio
    @async_httprettified
    async def test_auth_leak(self, client):
        httpretty.register_uri(
            httpretty.GET, "http://hackerz.py.invalid",
            body='expected')

        resp = await client.request('GET', "http://hackerz.py.invalid",
                           params={'foo': 'bar'})
        assert resp.status_code == 200
        assert resp.read() == b'expected'
        assert httpretty.last_request.querystring == {'foo': ['bar']}
        assert httpretty.last_request.headers.get('authorization') is None
    test_auth_leak.auth = BasicAuthenticator(host="swagger.py.invalid",
            username="unit", password='peekaboo')

