# ExploreBaduk GameServer
The game server designed for the ExploreBaduk website

Use Python >=3.7
Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate
make install
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
  - [x] time control
  - [ ] counting

#### WebSocket message exchange
##### Authorization
- [x] login 
- [x] logout

##### Challenge
- [x] create challenge
- [x] cancel challenge
- [x] join challenge
- [x] accept challenge
- [ ] decline challenge
- [ ] change request
- [ ] return change request

##### Play move
- [x] play move
- [x] make pass
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
