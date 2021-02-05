Messages from backend
=====================

Who Am I
--------
When:
    - after authorization

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
  - on **players.list** event

.. code-block:: json

    {
        "event": "players.list",
        "data": [
            {
                "status": "online",
                "user_id": 2,
                "friend": true,
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
                "friend": false,
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

Players Remove
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
