Messages from backend
=====================

Who Am I
--------
When:
    - as first message

.. code-block:: json

    {
        "event": "whoami",
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

Players List
------------
When:
  - after authorization

.. code-block:: json

    {
        "event": "players.list",
        "data": [
            {
                "status": "online",
                "user_id": 2,
                "username": "johndoe1",
                "first_name": "John",
                "last_name": "Doe#1",
                "email": "johndoe1@explorebaduk.com",
                "rating": 2039.00,
                "puzzle_rating": 1433.00,
                "avatar": null
            },
            {
                "status": "online",
                "user_id": 3,
                "username": "johndoe2",
                "first_name": "John",
                "last_name": "Doe#2",
                "email": "johndoe2@explorebaduk.com",
                "rating": 1252.00,
                "puzzle_rating": 432.00,
                "avatar": null
            }
        ]
    }

Players Add
-----------
When:
    - player authorizes

.. code-block:: json

    {
        "event": "players.add",
        "data": {
            "status": "online",
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

Player is offline
--------------
When:
    - player disconnects

.. code-block:: json

    {
        "event": "players.remove",
        "data": {
            "user_id": 2
        }
    }


Open game created
-----------
When:
    - player creates open game

.. code-block:: json

    {
        "event": "games.open.add",
        "data": {
            "user_id": 1,
            "game_setup": {
                "name": "My first game",
                "type": "ranked",
                "is_private": false
            },
            "rule_set": {
                "rules": "japanese",
                "board_size": 19
            },
            "time_settings": {
                "time_system": "byo-yomi",
                "main_time": 3600,
                "overtime": 30,
                "periods": 5,
                "stones": 1,
                "bonus": 0
            }
        }
    }


Open game cancelled
-----------
When:
    - game creator cancels the game or disconnects

.. code-block:: json

    {
        "event": "games.open.remove",
        "data": {"user_id": 1}
    }


Direct invite created
-----------
When:
    - player invites to play

.. code-block:: json

    {
        "event": "games.direct.add",
        "data": {
            "user_id": 1,
            "game_setup": {
                "name": "My first game",
                "type": "ranked",
                "is_private": false
            },
            "rule_set": {
                "rules": "japanese",
                "board_size": 19
            },
            "time_settings": {
                "time_system": "byo-yomi",
                "main_time": 3600,
                "overtime": 30,
                "periods": 5,
                "stones": 1,
                "bonus": 0
            }
        }
    }


Direct invite cancelled
-----------
When:
    - game creator cancels the invite or disconnects

.. code-block:: json

    {
        "event": "games.direct.remove",
        "data": {"user_id": 1}
    }
