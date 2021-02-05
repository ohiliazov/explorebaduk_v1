Messages from frontend
======================

Authorization
-------------
Should be sent as a first message.

.. code-block:: json

    {
        "event": "authorize",
        "data": "<auth_token>"
    }

Players List
------------
Asks backend to send players.list message with filtered players.

.. code-block:: json

    {
        "event": "players.list",
        "data": "<search_string>"
    }
