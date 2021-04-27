from typing import List

from fastapi import APIRouter, Depends

from explorebaduk.crud import DatabaseHandler
from explorebaduk.dependencies import current_user
from explorebaduk.models import UserModel
from explorebaduk.schemas import FriendList, User

router = APIRouter(tags=["me"])


@router.post("/me/whoami")
def check_authentication(user: UserModel = Depends(current_user)):
    return user.asdict()


@router.get("/me/followers", response_model=List[User])
def get_followers(user: UserModel = Depends(current_user)):
    with DatabaseHandler() as db:
        return [f.friend for f in db.get_following(user.user_id)]


@router.get("/me/following", response_model=List[User])
def get_following(user: UserModel = Depends(current_user)):
    with DatabaseHandler() as db:
        return [f.user for f in db.get_followers(user.user_id)]


@router.get("/me/friends", response_model=FriendList)
def get_friends(user: UserModel = Depends(current_user)):
    with DatabaseHandler() as db:
        pending = {f.friend for f in db.get_following(user.user_id)}
        waiting = {f.friend for f in db.get_followers(user.user_id)}

    return {
        "friends": pending & waiting,
        "pending": pending - waiting,
        "waiting": waiting - pending,
    }


@router.get("/me/challenges/incoming")
async def list_incoming_challenges(user: UserModel = Depends(current_user)):
    with DatabaseHandler() as db:
        return db.list_incoming_challenges(user.user_id)


@router.get("/me/challenges/outgoing")
async def list_outgoing_challenges(user: UserModel = Depends(current_user)):
    with DatabaseHandler() as db:
        return db.list_outgoing_challenges(user.user_id)
