# ExploreBaduk GameServer
The game server designed for the ExploreBaduk website

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

#### General TODO:
  - [ ] WebSocket message exchange
  - [x] sgf navigation
  - [x] board representation
  - [ ] game play
  - [ ] time control
  - [ ] counting
  
#### WebSocket message exchange
##### Authorization
- [x] login 
- [x] logout

##### Challenge
- [x] create challenge
- [ ] cancel challenge
- [x] join challenge
- [ ] accept challenge
- [ ] decline challenge
- [ ] change request
- [ ] return change request

##### Play move
- [ ] play move
- [ ] make pass
- [ ] resign

##### Undo move
- [ ] request undo
- [ ] accept undo
- [ ] decline undo
    
##### Scoring
- [ ] mark dead
- [ ] mark alive
- [ ] done
- [ ] decline
