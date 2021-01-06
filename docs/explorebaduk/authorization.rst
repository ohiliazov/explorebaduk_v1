Authorization
===============
Authorization enables users to play.
If user is not authorized, he is treated as guest.

1. Authorized vs. guest
------------------------------
Authorized users can view, play games, chat etc.

Unauthorized users, or `guests`, can only view.

2. Authorized HTTP request
-------------------------------------
To make authorized HTTP requests, add `Authorization` header with active `Authorization Token`.

3. Authorized WebSocket connection
----------------------------------
To make authorized WebSocket requests, send authorization message in the format:

.. code-block:: json

    {
        "event": "authorize",
        "data": {
            "token": "<auth_token>"
        }
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
