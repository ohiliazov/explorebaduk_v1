Challenge List
==============


Messages from server
--------------------


When new `challenge <models.html#challenge>`_ is created,
all connections receive message to add player to the list of challenges.

.. code-block:: json

    {
        "event": "challenges.add",
        "data": {
            "user_id": 777,
            "game_setup": {
                "name": "My Game 777",
                "type": "ranked",
                "is_private": false
            },
            "rule_set": {
                "rules": "japanese",
                "board_size": 19
            },
            "time_settings": {
                "time_system": "canadian",
                "main_time": 1800,
                "overtime": 300,
                "periods": 1,
                "stones": 20,
                "bonus": 0
        }
    }


When challenge is cancelled for any reason.

.. code-block:: json

    {
        "event": "challenges.remove",
        "data": {
            "user_id": 777
        }
    }
