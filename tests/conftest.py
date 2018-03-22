#!/usr/bin/env python

import httpretty as htpr
import pytest
from aioswagger11.client import SwaggerClient
from aioswagger11.http_client import AsynchronousHttpClient

@pytest.fixture
def httpretty(request, event_loop):
    """Setup httpretty; create ARI client.
        """
    #super(AriTestCase, self).setUp()
    htpr.enable()
    request.instance.setUp(event_loop)

    yield 123

    request.instance.tearDown(event_loop)
    htpr.disable()
    htpr.reset()

@pytest.fixture
def client(event_loop, request):
    htpr.enable()
    auth = getattr(request.function,'auth',None)
    client = AsynchronousHttpClient(loop=event_loop, auth=auth)
    yield client
    event_loop.run_until_complete(client.close())
    htpr.disable()

@pytest.fixture
def uut(event_loop):
    # Default handlers for all swagger.py access
    htpr.enable()
    resource_listing = {
        "swaggerVersion": "1.1",
        "basePath": "http://swagger.py/swagger-test",
        "apis": [
            {
                "path": "/api-docs/pet.json",
                "description": "Test loader when missing a file",
                "api_declaration": {
                    "swaggerVersion": "1.1",
                    "basePath": "http://swagger.py/swagger-test",
                    "resourcePath": "/pet.json",
                    "apis": [
                        {
                            "path": "/pet",
                            "operations": [
                                {
                                    "httpMethod": "GET",
                                    "nickname": "listPets"
                                },
                                {
                                    "httpMethod": "POST",
                                    "nickname": "createPet",
                                    "parameters": [
                                        {
                                            "name": "name",
                                            "paramType": "query",
                                            "dataType": "string",
                                            "required": True
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "path": "/pet/find",
                            "operations": [
                                {
                                    "httpMethod": "GET",
                                    "nickname": "findPets",
                                    "parameters": [
                                        {
                                            "name": "species",
                                            "paramType": "query",
                                            "dataType": "string",
                                            "allowMultiple": True
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "path": "/pet/{petId}",
                            "operations": [
                                {
                                    "httpMethod": "DELETE",
                                    "nickname": "deletePet",
                                    "parameters": [
                                        {
                                            "name": "petId",
                                            "paramType": "path"
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                    "models": {}
                }
            }
        ]
    }

    client = SwaggerClient(url=resource_listing)
    event_loop.run_until_complete(client.init())
    yield client
    event_loop.run_until_complete(client.close())

    htpr.disable()

