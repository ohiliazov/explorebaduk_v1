from fastapi import APIRouter, Depends

from explorebaduk.crud import get_friendships
from explorebaduk.dependencies import get_current_user
from explorebaduk.models import UserModel
from explorebaduk.schemas import FriendListOut

router = APIRouter(prefix="/friends")


@router.get("", response_model=FriendListOut)
def get_friends(user: UserModel = Depends(get_current_user)):
    pending, waiting = set(), set()

    for user_id, friend_id in get_friendships(user.user_id):
        if friend_id != user.user_id:
            pending.add(friend_id)
        elif user_id != user.user_id:
            waiting.add(user_id)

    return {
        "friends": pending & waiting,
        "pending": pending - waiting,
        "waiting": waiting - pending,
    }


@router.get(
    "/{user_id}",
    response_model=FriendListOut,
    response_model_exclude_none=True,
    dependencies=[Depends(get_current_user)],
)
def get_user_friends(user_id: int):
    friends = set()
    friendships = get_friendships(user_id)
    for user_id, friend_id in friendships:
        if (friend_id, user_id) in friendships:
            friends.add(friend_id)

    return {"friends": sorted(friends)}
