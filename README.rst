About
-----

asyncswagger11 is an anyio-compatible clone of swagger.py, capable of
understanding Swagger 1.1 definitions (only).

As swagger has been renamed to OpenAPI which by now has version 3.0
(and has an actual specification – unlike Swagger 1.1) this library is
(mostly) only usable with Asterisk, which still uses Swagger 1.1
declarations.

Asyncswagger11 supports a WebSocket extension, allowing a WebSocket to
be documented, and auto-generated WebSocket client code.

from swagger.py:
================

Swagger.py is a Python library for using
`Swagger <https://developers.helloreverb.com/swagger/>`__ defined APIs.

Swagger itself is best described on the Swagger home page:

    Swagger is a specification and complete framework implementation for
    describing, producing, consuming, and visualizing RESTful web
    services.

The `Swagger
specification <https://github.com/wordnik/swagger-core/wiki>`__ defines
how APIs may be described using Swagger.

Usage
-----

Install the latest release from PyPI.

::

    $ sudo pip install asyncswagger11

Or install from source using the ``setup.py`` script.

::

    $ sudo ./setup.py install

API
===

asyncswagger11 will dynamically build an object model from a Swagger-enabled
RESTful API.

Here is a simple example using the `Asterisk REST
Interface <https://wiki.asterisk.org/wiki/display/AST/Asterisk+12+ARI>`__

.. code:: Python

    #!/usr/bin/env python3

    import json
    import anyio

    from asyncswagger11.client import SwaggerClient
    from asyncswagger11.http_client import AsynchronousHttpClient

    http_client = AsynchronousHttpClient()
    http_client.set_api_key('localhost', 'hey:peekaboo')

    async def run(ari,msg_json):
        channelId = msg_json['channel']['id']
        await ari.channels.answer(channelId=channelId)
        await ari.channels.play(channelId=channelId,
                        media='sound:hello-world')
        # In a real program you should wait for the PlaybackFinished event instead
        await anyio.sleep(3)
        await ari.channels.continueInDialplan(channelId=channelId)

    async def main():
        ari = SwaggerClient(
            "http://localhost:8088/ari/api-docs/resources.json",
            http_client=http_client)

        ws = ari.events.eventWebsocket(app='hello')

        async for msg in ws:
            if not isinstance(msg, WebsocketDataMessage):
                break
            elif not isinstance(msg, WebsocketTextMessage):
                continue # ignore bytes

            msg_json = json.loads(msg.data)
            if msg_json['type'] == 'StasisStart':
                await nursery.start_soon(run,ari,msg_json)

    if __name__ == "__main__":
        anyio.run(main)
   

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
    $ ./setup.py pytest    # run unit tests
    $ ./setup.py bdist_egg # build distributable


Testing
=======

Simply run ``python3 setup.py pytest``.

Note that standalone-testing this module currently is not possible.
Previous versions required a hacked version of httpretty.

TODO: use a local server instead.


License
-------

Copyright (c) 2013, Digium, Inc.
Copyright (c) 2018, Matthias Urlichs

asyncswagger11 is licensed with a `BSD 3-Clause
License <http://opensource.org/licenses/BSD-3-Clause>`__.

The current author humbly requests that you share any further bug fixes or
enhancements to this code.

