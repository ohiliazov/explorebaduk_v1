# ExploreBaduk GameServer
The game server designed for the ExploreBaduk website

Use Python >=3.8
Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate
make install
```

Run server within your python virtual environment:
```bash
python run_api.py --host localhost --port 8080 --auto-reload

```

Example to interactively connect to websocket feed:
```bash
python -m websockets ws://localhost:8080/players
```
