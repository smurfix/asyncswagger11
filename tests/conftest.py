#!/usr/bin/env python

import pytest
from asyncswagger11.client import SwaggerClient
from asyncswagger11.http_client import AsynchronousHttpClient

@pytest.fixture
def httpretty(request):
    """Setup httpretty; create ARI client.
        """
    #super(AriTestCase, self).setUp()
    request.instance.setUp()

    yield 123

    request.instance.tearDown()

@pytest.fixture
async def client(request):
    auth = getattr(request.function,'auth',None)
    client = AsynchronousHttpClient(auth=auth)
    yield client
    await client.close()

@pytest.fixture
async def uut():
    # Default handlers for all swagger.py access
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
    await client.init()
    yield client
    await client.close()


