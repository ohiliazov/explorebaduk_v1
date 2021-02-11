from typing import Optional

from fastapi import APIRouter, Depends

from explorebaduk.crud import get_friendships, get_players_list
from explorebaduk.dependencies import get_user_from_header
from explorebaduk.models import UserModel

router = APIRouter(
    prefix="/players",
)


@router.get("/")
def get_players(q: str = None):
    return [player.as_dict() for player in get_players_list(q)]


@router.get("/my-friends")
def get_friends(user: Optional[UserModel] = Depends(get_user_from_header)):
    friendships = get_friendships(user)
    mutual, pending, waiting = set(), set(), set()
    for user_id, friend_id in friendships:
        if user_id == user.user_id:
            if (friend_id, user_id) in friendships:
                mutual.add(friend_id)
            else:
                pending.add(friend_id)
        else:
            if (friend_id, user_id) not in friendships:
                waiting.add(user_id)
    return {
        "mutual": mutual,
        "pending": pending,
        "waiting": waiting,
    }
