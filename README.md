# eb-server
The game server designed for Explore Baduk

Python 3.6 virtual environment:
```bash
python3.6 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run server within your python virtual environment:
```bash
python manage.py
```

To interactively connect to server:
```bash
python -m websockets ws://localhost:8080
```
