from fastapi import APIRouter, Depends

from ..crud import DatabaseHandler
from ..dependencies import current_user
from ..models import UserModel
from ..schemas import FriendList

router = APIRouter(prefix="/friends", tags=["friends"])


@router.get("", response_model=FriendList)
def get_friends(user: UserModel = Depends(current_user)):
    with DatabaseHandler() as db:
        return {
            "following": [f.friend_id for f in db.get_following(user.user_id)],
            "followers": [f.user_id for f in db.get_followers(user.user_id)],
        }


@router.get(
    "/{user_id}",
    response_model=FriendList,
    response_model_exclude_none=True,
    dependencies=[Depends(current_user)],
)
def get_user_friends(user_id: int):
    with DatabaseHandler() as db:
        return {
            "following": [f.friend_id for f in db.get_following(user_id)],
            "followers": [f.user_id for f in db.get_followers(user_id)],
        }
