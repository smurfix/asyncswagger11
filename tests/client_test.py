#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2018, Matthias Urlichs
#

"""Swagger client tests.
"""

import httpretty
import pytest

from aioswagger11.client import SwaggerClient

from aiohttp.web_exceptions import HTTPNoContent, HTTPCreated

# noinspection PyDocstring
class TestClient:

    def test_bad_operation(self, uut):
        with pytest.raises(AttributeError):
            uut.pet.doesNotExist()

    @pytest.mark.asyncio
    async def test_bad_param(self, uut):
        with pytest.raises(TypeError):
            await uut.pet.listPets(doesNotExist='asdf')

    @pytest.mark.asyncio
    async def test_missing_required(self, uut):
        with pytest.raises(TypeError):
            await uut.pet.createPet()

    @pytest.mark.asyncio
    async def test_get(self, uut):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/swagger-test/pet",
            content_type="application/json",
            body='[]')

        resp = await uut.pet.listPets()
        assert resp.status == 200
        assert (await resp.json()) == []

    @pytest.mark.asyncio
    async def test_multiple(self, uut):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/swagger-test/pet/find",
            content_type="application/json",
            body='[]')

        resp = await uut.pet.findPets(species=['cat', 'dog'])
        assert resp.status == 200
        assert (await resp.json()) == []
        assert httpretty.last_request().querystring == {'species': ['cat,dog']}

    @pytest.mark.asyncio
    async def test_post(self, uut):
        httpretty.register_uri(
            httpretty.POST, "http://swagger.py/swagger-test/pet",
            status=HTTPCreated.status_code,
            content_type="application/json",
            body='{"id": 1234, "name": "Sparky"}')

        resp = await uut.pet.createPet(name='Sparky')
        assert resp.status == HTTPCreated.status_code
        assert (await resp.json()) == {"id": 1234, "name": "Sparky"}
        assert httpretty.last_request().querystring == {'name': ['Sparky']}

    @pytest.mark.asyncio
    async def test_delete(self, uut):
        httpretty.register_uri(
            httpretty.DELETE, "http://swagger.py/swagger-test/pet/1234",
            status=HTTPNoContent.status_code)

        resp = await uut.pet.deletePet(petId=1234)
        assert resp.status == HTTPNoContent.status_code
        assert (await resp.read()) == b''

