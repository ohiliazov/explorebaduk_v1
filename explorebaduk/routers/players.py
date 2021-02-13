from typing import List, Optional

from fastapi import APIRouter, Depends

from explorebaduk.crud import get_friendships, get_players_list
from explorebaduk.dependencies import get_user_from_header
from explorebaduk.models import UserModel
from explorebaduk.schemas import MyFriendsOut, PlayerOut

router = APIRouter(
    prefix="/players",
)


@router.get("/", response_model=List[PlayerOut])
def get_players(q: str = None):
    return [player.as_dict() for player in get_players_list(search_string=q)]


@router.get("/my-friends", response_model=MyFriendsOut)
def get_friends(user: Optional[UserModel] = Depends(get_user_from_header)):
    friendships = get_friendships(user)
    mutual, sent, received = set(), set(), set()
    for user_id, friend_id in friendships:
        if user_id == user.user_id:
            if (friend_id, user_id) in friendships:
                mutual.add(friend_id)
            else:
                sent.add(friend_id)
        else:
            if (friend_id, user_id) not in friendships:
                received.add(user_id)
    return {
        "mutual": mutual,
        "sent": sent,
        "received": received,
    }
