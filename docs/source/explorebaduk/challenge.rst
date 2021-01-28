Challenge
=========


Messages from server
--------------------


When the `challenge <models.html#challenge>`_ is set.

.. code-block:: json

    {
        "event": "challenge.set",
        "data": {
            "message": "Challenge set"
        }
    }


When the `challenge <models.html#challenge>`_ is unset.

.. code-block:: json

    {
        "event": "challenge.unset",
        "data": {
            "message": "Challenge unset"
        }
    }

When a player joins the `challenge <models.html#challenge>`_.

.. code-block:: json

    {
        "event": "challenge.join",
        "data": {
            "user_id": 93,
            "username": "johndoe92",
            "first_name": "John#92",
            "last_name": "Doe#92",
            "email": "johndoe92@explorebaduk.com",
            "rating": 2747.00,
            "puzzle_rating": 1690.00,
            "avatar": null
        }
    }

When a player leaves the `challenge <models.html#challenge>`_.

.. code-block:: json

    {
        "event": "challenge.leave",
        "data": {
            "user_id": 93
        }
    }
