from fastapi import APIRouter, Depends

from explorebaduk.crud import get_friendships
from explorebaduk.dependencies import get_current_user
from explorebaduk.models import UserModel
from explorebaduk.schemas import FriendListOut

router = APIRouter(prefix="/friends")


@router.get("", response_model=FriendListOut)
def get_friends(user: UserModel = Depends(get_current_user)):
    friends_out, friends_in = set(), set()

    for user_id, friend_id in get_friendships(user.user_id):
        if friend_id != user.user_id:
            friends_out.add(friend_id)
        elif user_id != user.user_id:
            friends_in.add(user_id)

    return {
        "friends": friends_out & friends_in,
        "friends_out": friends_out - friends_in,
        "friends_in": friends_in - friends_out,
    }


@router.get("/{user_id}", response_model=FriendListOut)
def get_user_friends(user_id: int, user: UserModel = Depends(get_current_user)):
    friends_out, friends_in = set(), set()

    for user_id, friend_id in get_friendships(user_id):
        if friend_id != user.user_id:
            friends_out.add(friend_id)
        elif user_id != user.user_id:
            friends_in.add(user_id)

    return {
        "user_id": user_id,
        "friends": sorted(friends_in & friends_out),
        "friends_out": sorted(friends_out - friends_in),
        "friends_in": sorted(friends_in - friends_out),
    }
