# API documentation
The documentation contains API
##  Players Feed
### Description
Players feed shows users online
### Endpoint URL
```
ws://<host>:<port>/players/feed
```
#### Authorization header
```
Authorization=<token>
```
### Server messages
#### User login info
Sent once per connection.
To authorize, provide valid Authorization header.
##### Authorized player
```json
{
    "status": "login",
    "player": {
        "player_id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@email.com",
        "rating": 1200.00,
        "puzzle_rating": 1000.00
    }
}
```
##### Not authorized (guest) player
```json
{
    "status": "login",
    "player": null
}
```
#### Player online
Sent each time player connects to the feed.
```json
{
    "status": "online",
    "player": {
        "player_id": 2,
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "janedoe@email.com",
        "rating": 1700.00,
        "puzzle_rating": 1400.00
    }
}
```
##### Player offline
Sent each time player disconnects from the feed.
```json
{
    "status": "offline",
    "player_id": 3
}
```
#### Client messages
##### Refresh player list
Asks server to resend "Player online" messages for each player.
```json
{
    "action": "refresh"
}
```
