#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2018, Matthias Urlichs
#

"""Swagger client tests.
"""

from mocket.plugins.httpretty import httpretty,async_httprettified
import pytest

# HTTP status codes
CREATED=201
NO_CONTENT=204

from asyncswagger11.client import SwaggerClient

# noinspection PyDocstring
class TestClient:

    def test_bad_operation(self, uut):
        with pytest.raises(AttributeError):
            uut.pet.doesNotExist()

    @pytest.mark.anyio
    @async_httprettified
    async def test_bad_param(self, uut):
        with pytest.raises(TypeError):
            await uut.pet.listPets(doesNotExist='asdf')

    @pytest.mark.anyio
    @async_httprettified
    async def test_missing_required(self, uut):
        with pytest.raises(TypeError):
            await uut.pet.createPet()

    @pytest.mark.anyio
    @async_httprettified
    async def test_get(self, uut):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py.invalid/swagger-test/pet",
            content_type="application/json",
            body='[]')

        resp = await uut.pet.listPets()
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.anyio
    @async_httprettified
    async def test_multiple(self, uut):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py.invalid/swagger-test/pet/find",
            content_type="application/json",
            body='[]')

        resp = await uut.pet.findPets(species=['cat', 'dog'])
        assert resp.status_code == 200
        assert resp.json() == []
        assert httpretty.last_request.querystring == {'species': ['cat,dog']}

    @pytest.mark.anyio
    @async_httprettified
    async def test_post(self, uut):
        httpretty.register_uri(
            httpretty.POST, "http://swagger.py.invalid/swagger-test/pet",
            status=CREATED,
            content_type="application/json",
            body='{"id": 1234, "name": "Sparky"}')

        resp = await uut.pet.createPet(name='Sparky')
        assert resp.status_code == CREATED
        assert resp.json() == {"id": 1234, "name": "Sparky"}
        assert httpretty.last_request.querystring == {'name': ['Sparky']}

    @pytest.mark.anyio
    @async_httprettified
    async def test_delete(self, uut):
        httpretty.register_uri(
            httpretty.DELETE, "http://swagger.py.invalid/swagger-test/pet/1234",
            status=NO_CONTENT)

        resp = await uut.pet.deletePet(petId=1234)
        assert resp.status_code == NO_CONTENT
        assert resp.read() == b''

