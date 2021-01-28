Player List
===========

Messages from server
--------------------

When new `player <models.html#player>`_ authorizes, all connections receive message to add player to the list of online players.
If the player is already online, the message is not repeated.

.. code-block:: json

    {
        "event": "players.add",
        "data": {
            "user_id": 2,
            "friend": true,
            "username": "johndoe1",
            "first_name": "John",
            "last_name": "Doe#1",
            "email": "johndoe1@explorebaduk.com",
            "rating": 2039.00,
            "puzzle_rating": 1433.00,
            "avatar": null
        }
    }

When the `player <models.html#player>`_ disconnects, all connections receive message to remove player from the list of online players.
If the player is still online from other devices, the message is not repeated.

.. code-block:: json

    {
        "event": "players.remove",
        "data": {
            "user_id": 2
        }
    }

Messages from client
--------------------

User can refresh players list by sending refresh message.

.. code-block:: json

    {
        "event": "refresh"
    }
