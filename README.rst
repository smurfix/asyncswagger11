About
-----

Swagger.py is a Python library for using
`Swagger <https://developers.helloreverb.com/swagger/>`__ defined API's.

Swagger itself is best described on the Swagger home page:

    Swagger is a specification and complete framework implementation for
    describing, producing, consuming, and visualizing RESTful web
    services.

The `Swagger
specification <https://github.com/wordnik/swagger-core/wiki>`__ defines
how API's may be described using Swagger.

Swagger.py also supports a WebSocket extension, allowing a WebSocket to
be documented, and auto-generated WebSocket client code.

Usage
-----

Install the latest release from PyPI.

::

    $ sudo pip install aioswagger11

Or install from source using the ``setup.py`` script.

::

    $ sudo ./setup.py install

API
===

Swagger.py will dynamically build an object model from a Swagger-enabled
RESTful API.

Here is a simple example using the `Asterisk REST
Interface <https://wiki.asterisk.org/wiki/display/AST/Asterisk+12+ARI>`__

.. code:: Python

    #!/usr/bin/env python3

    import json
    import asyncio
    import aiohttp

    from aioswagger11.client import SwaggerClient
    from aioswagger11.http_client import AsynchronousHttpClient

    http_client = AsynchronousHttpClient()
    http_client.set_api_key('localhost', 'hey:peekaboo')

    async def run(ari,msg_json):
        channelId = msg_json['channel']['id']
        await ari.channels.answer(channelId=channelId)
        await ari.channels.play(channelId=channelId,
                        media='sound:hello-world')
        # In a real program you should wait for the PlaybackFinished event instead
        await asyncio.sleep(3)
        await ari.channels.continueInDialplan(channelId=channelId)

    async def main():
        ari = SwaggerClient(
            "http://localhost:8088/ari/api-docs/resources.json",
            http_client=http_client)

        ws = ari.events.eventWebsocket(app='hello')

        async for msg_str in ws:
            if msg.type in {aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSING}:
                break
            elif msg.type != aiohttp.WSMsgType.TEXT:
                continue # ignore

            msg_json = json.loads(msg_str)
            if msg_json['type'] == 'StasisStart':
                asyncio.ensure_future(run(ari,msg_json))

    if __name__ == "__main__":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())

swagger-codegen
===============

There are the beginnings of a Mustache-based code generator, but it's
not functional... yet.

.. Inspired by the original [swagger-codegen][] project, templates are
   written using [Mustache][] templates ([Pystache][], specifically).
   There are several important differences.

    * The model that is fed into the mustache templates is almost
      identical to Swagger's API resource listing and API declaration
      model. The differences are listed [below](#model).
    * The templates themselves are completely self contained, with the
      logic to enrich the model being specified in `translate.py` in the
      same directory as the `*.mustache` files.

Data model
==========

The data model presented by the ``swagger_model`` module is nearly
identical to the original Swagger API resource listing and API
declaration. This means that if you add extra custom metadata to your
docs (such as a ``_author`` or ``_copyright`` field), they will carry
forward into the object model. I recommend prefixing custom fields with
an underscore, to avoid collisions with future versions of Swagger.

There are a few meaningful differences.

-  Resource listing
-  The ``file`` and ``base_dir`` fields have been added, referencing the
   original ``.json`` file.
-  The objects in a ``resource_listing``'s ``api`` array contains a
   field ``api_declaration``, which is the processed result from the
   referenced API doc.
-  API declaration
-  A ``file`` field has been added, referencing the original ``.json``
   file.

Development
-----------

The code is documented using `Sphinx <http://sphinx-doc.org/>`__, which
allows `IntelliJ IDEA <http://confluence.jetbrains.net/display/PYH/>`__
to do a better job at inferring types for autocompletion.

To keep things isolated, I also recommend installing (and using)
`virtualenv <http://www.virtualenv.org/>`__.

::

    $ sudo pip install virtualenv
    $ mkdir -p ~/virtualenv
    $ virtualenv ~/virtualenv/swagger
    $ . ~/virtualenv/swagger/bin/activate

`Setuptools <http://pypi.python.org/pypi/setuptools>`__ is used for
building. `Pytest <http://pytest.readthedocs.org/en/latest/>`__ is used
for unit testing, with the `coverage
<http://nedbatchelder.com/code/coverage/>`__ plugin installed to
generated code coverage reports. Pass ``--with-coverage`` to generate
the code coverage report. HTML versions of the reports are put in
``cover/index.html``.

::

    $ ./setup.py develop   # prep for development (install deps, launchers, etc.)
    $ ./setup.py nosetests # run unit tests
    $ ./setup.py bdist_egg # build distributable



License
-------

Copyright (c) 2013, Digium, Inc.
Copyright (c) 2018, Matthias Urlichs

Swagger.py is licensed with a `BSD 3-Clause
License <http://opensource.org/licenses/BSD-3-Clause>`__.

