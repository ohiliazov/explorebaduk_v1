from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import current_user_online
from ..models import UserModel
from ..schemas import GameSetup
from ..shared import GameRequests

router = APIRouter(prefix="/game-invites", tags=["game-invites"])


@router.post("/{opponent_id}", response_model=GameSetup)
async def create_game_invite(opponent_id: int, game: GameSetup, user: UserModel = Depends(current_user_online)):
    if opponent_id in GameRequests.get_direct_invites(user.user_id):
        raise HTTPException(400, "Direct invite to this user already exists")

    await GameRequests.create_direct_invite(opponent_id, user, game)
    return game


@router.delete("/{opponent_id}")
async def cancel_game_invite(opponent_id: int, user: UserModel = Depends(current_user_online)):
    if opponent_id not in GameRequests.get_direct_invites(user.user_id):
        raise HTTPException(404, "Direct invite not found")

    await GameRequests.remove_direct_invite(opponent_id, user)
    return {"message": "Direct invite cancelled"}


@router.post("/{opponent_id}/accept")
async def accept_game_invite(
    opponent_id: int,
    user: UserModel = Depends(current_user_online),
):
    if user.user_id not in GameRequests.get_direct_invites(opponent_id):
        raise HTTPException(404, "Invite not found")

    # create game model here
    await GameRequests.accept_direct_invite(opponent_id, user)
    return {"message": "Game invite accepted"}


@router.delete("/{opponent_id}/accept")
async def reject_game_invite(
    opponent_id: int,
    user: UserModel = Depends(current_user_online),
):
    if user.user_id not in GameRequests.get_direct_invites(opponent_id):
        raise HTTPException(404, "Invite not found")

    await GameRequests.reject_direct_invite(opponent_id, user)
    return {"message": "Game invite rejected"}
