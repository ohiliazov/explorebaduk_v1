WebSocket Message Format
========================

All messages in WebSocket are JSON in format:

.. code-block:: json

    {
        "event": "event.name",
        "data": {
            "key": "value"
        }
    }

- ``event``: describes the event type
- ``data``: contains data

Examples
--------

.. code-block:: json

    {
        "event": "authorize",
        "data": {
            "token": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ000000000000"
        }
    }

.. code-block:: json

    {
        "event": "refresh"
    }

.. code-block:: json

    {
        "event": "auth.whoami",
        "data": {
            "user_id": 2,
            "username": "johndoe1",
            "first_name": "John",
            "last_name": "Doe#1",
            "email": "johndoe1@explorebaduk.com",
            "rating": 2039.00,
            "puzzle_rating": 1433.00,
            "avatar": null
        }
    }
