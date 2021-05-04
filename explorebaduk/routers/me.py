from typing import List

from fastapi import APIRouter, Depends

from explorebaduk.database import DatabaseHandler
from explorebaduk.dependencies import current_user, db_handler
from explorebaduk.models import UserModel
from explorebaduk.schemas import FriendList, User

router = APIRouter(tags=["me"])


@router.get("/me/whoami", response_model=User)
def check_authentication(user: UserModel = Depends(current_user)):
    return user


@router.get("/me/followers", response_model=List[User])
def get_followers(
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(db_handler),
):
    return [f.friend for f in db.get_followers(user.user_id)]


@router.get("/me/following", response_model=List[User])
def get_following(
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(db_handler),
):
    return [f.user for f in db.get_followers(user.user_id)]


@router.get("/me/blacklist", response_model=List[User])
def get_blocked_users(
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(db_handler),
):
    return [f.user for f in db.get_blocked_users(user.user_id)]


@router.get("/me/friends", response_model=FriendList)
def get_friends(
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(db_handler),
):
    following = {f.friend_id for f in db.get_following(user.user_id)}
    followers = {f.user_id for f in db.get_followers(user.user_id)}
    blacklist = {b.blocked_user_id for b in db.get_blocked_users(user.user_id)}

    return {
        "mutual": followers & following,
        "following": following - followers,
        "followers": followers - following,
        "blacklist": blacklist,
    }


@router.get("/me/challenges/incoming")
async def list_incoming_challenges(
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(db_handler),
):
    return db.get_challenges_to_user(user.user_id)


@router.get("/me/challenges/outgoing")
async def list_outgoing_challenges(
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(db_handler),
):
    return db.get_challenges_from_user(user.user_id)
