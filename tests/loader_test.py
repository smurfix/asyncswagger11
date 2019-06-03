#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2018, Matthias Urlichs
#

import pytest
import asyncswagger11

from asyncswagger11 import swagger_model


class FakeProcessor(swagger_model.SwaggerProcessor):
    def process_resource_listing(self, resources, context):
        resources['processed'] = True


class TestLoader:
    @pytest.mark.anyio
    async def test_simple(self):
        uut = await asyncswagger11.load_file('test-data/1.1/simple/resources.json')
        assert uut['swaggerVersion'] == '1.1'
        decl = uut['apis'][0]['api_declaration']
        assert len(decl['models']) == 1
        assert len(decl['models']['Simple']['properties']) == 1

    @pytest.mark.anyio
    async def test_processor(self):
        uut = await asyncswagger11.load_file('test-data/1.1/simple/resources.json',
                                  processors=[FakeProcessor()])
        assert uut['swaggerVersion'] == '1.1'
        assert uut['processed'] is True

    @pytest.mark.anyio
    async def test_missing(self):
        try:
            await asyncswagger11.load_file(
                'test-data/1.1/missing_resource/resources.json')
            pytest.fail("Expected load failure b/c of missing file")
        except IOError:
            pass


if __name__ == '__main__':
    unittest.main()
