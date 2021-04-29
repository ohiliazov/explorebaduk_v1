from typing import List

from fastapi import APIRouter, Depends, HTTPException

from explorebaduk.crud import DatabaseHandler
from explorebaduk.dependencies import current_user, get_db_session
from explorebaduk.managers import UsersManager
from explorebaduk.models import UserModel
from explorebaduk.schemas import User

router = APIRouter(tags=["players"])


@router.get("/players", response_model=List[User])
def list_players(
    q: str = None,
    online: bool = False,
    db: DatabaseHandler = Depends(get_db_session),
):
    players = db.get_users(q=q)

    if online:
        players = list(filter(UsersManager.is_online, players))

    return players


@router.get("/players/{player_id}", response_model=User)
def get_player(player_id: int, db: DatabaseHandler = Depends(get_db_session)):
    return db.get_user_by_id(player_id)


@router.post("/players/{player_id}/follow")
def follow_player(
    player_id: int,
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(get_db_session),
):
    if not db.get_user_by_id(player_id):
        raise HTTPException(404, "User not found")

    if db.get_friendship(user.user_id, player_id):
        raise HTTPException(400, "User is already your friend")

    if blacklist := db.get_blocked_user(user.user_id, player_id):
        db.session.delete(blacklist)

    db.follow_user(user.user_id, player_id)

    return {"message": "Followed user"}


@router.post("/players/{player_id}/unfollow")
def unfollow_player(
    player_id: int,
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(get_db_session),
):
    if not db.get_user_by_id(player_id):
        raise HTTPException(404, "User not found")

    if friendship := db.get_friendship(user.user_id, player_id):
        db.session.delete(friendship)
        return {"message": "Unfollowed user"}

    raise HTTPException(400, "User is not your friend")


@router.post("/players/{player_id}/block")
def block_player(
    player_id: int,
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(get_db_session),
):
    if not db.get_user_by_id(player_id):
        raise HTTPException(404, "User not found")

    if friendship := db.get_friendship(user.user_id, player_id):
        db.session.delete(friendship)

    if db.get_blocked_user(user.user_id, player_id):
        raise HTTPException(400, "User is already blocked")

    db.block_user(user.user_id, player_id)

    return {"message": "Blocked user"}


@router.post("/players/{player_id}/unblock")
def unblock_player(
    player_id: int,
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(get_db_session),
):
    if not db.get_user_by_id(player_id):
        raise HTTPException(404, "User not found")

    if blacklist := db.get_blocked_user(user.user_id, player_id):
        db.session.delete(blacklist)
        return {"message": "Unblocked user"}

    raise HTTPException(400, "User is not blocked")
