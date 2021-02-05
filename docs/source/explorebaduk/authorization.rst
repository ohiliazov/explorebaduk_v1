Authorization
===============
Authorization enables users to play.
If user is not authorized, he is treated as guest.

The websocket connection expects first message to be in the format:

.. code-block:: json

    {
        "event": "authorize",
        "data": "<auth_token>"
    }

The response of successful authorization:

.. code-block:: json

    {
        "event": "auth.whoami",
        "data": {
            "user_id": "<user_id>"
        }
    }

The response of unsuccessful authorization:

.. code-block:: json

    {
        "event": "auth.whoami",
        "data": null
    }
