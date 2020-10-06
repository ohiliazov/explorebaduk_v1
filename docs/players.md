# API documentation
The documentation contains API
##  Players Feed
### Description
Players feed shows users online
### Endpoint URL
```
ws://<host>:<port>/players
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
        "user_id": 1,
        "username": "johndoe1",
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
        "user_id": 2,
        "username": "janedoe2",
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
    "player": {
        "user_id": 1,
        "username": "johndoe1",
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@email.com",
        "rating": 1200.00,
        "puzzle_rating": 1000.00
    }
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
