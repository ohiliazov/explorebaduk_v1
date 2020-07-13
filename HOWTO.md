Python 3.8 is required.

Set your database URI in config files

```bash
DATABASE_URI="sqlite:///explorebaduk.sqlite3"
```

Before anything run

```bash
python3.8 -m venv venv
source venv/bin/activate
make install
```

Initialize test database and pass database URI:
```bash
make init_db
```

To run the server:
```bash
python run_api.py --host localhost --port 8080 --auto-reload
```

Now you can get users from:
```GET http://<host>:<port>/players/<player_id>```

WebSocket feed for players:
```ws://<host>:<port>/players```

To authenticate, you need to pass Authorization header with token as a value with initial HTTP request
