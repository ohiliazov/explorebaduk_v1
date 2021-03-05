from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import current_user_online
from ..helpers import Notifier
from ..models import UserModel
from ..schemas import GameInviteIn
from ..shared import GAME_INVITES

router = APIRouter()


@router.post("/game-invites/{opponent_id}", response_model=GameInviteIn)
async def create_game_invite(
    opponent_id: int, game: GameInviteIn, user: UserModel = Depends(current_user_online)
):
    direct_invites = GAME_INVITES[user.user_id]

    if opponent_id in direct_invites:
        raise HTTPException(400, "Direct invite to this user already exists")

    direct_invites[opponent_id] = game.dict()
    await Notifier.game_invite_created(opponent_id, user, game)

    return game


@router.delete("/game-invites/{opponent_id}")
async def cancel_game_invite(
    opponent_id: int, user: UserModel = Depends(current_user_online)
):
    direct_invites = GAME_INVITES[user.user_id]

    if opponent_id not in direct_invites:
        raise HTTPException(404, "Direct invite not found")

    direct_invites.pop(opponent_id)
    await Notifier.game_invite_cancelled(opponent_id, user)

    return {"message": "Direct invite cancelled"}


@router.post("/game-invites/{opponent_id}/accept")
async def accept_game_invite(
    opponent_id: int,
    user: UserModel = Depends(current_user_online),
):
    opponent_invites = GAME_INVITES[opponent_id]
    if user.user_id not in opponent_invites:
        raise HTTPException(404, "Invite not found")

    # create game model here
    await Notifier.game_invite_accepted(opponent_id, user)

    return {"message": "Game invite accepted"}


@router.post("/game-invites/{opponent_id}/reject")
async def reject_game_invite(
    opponent_id: int,
    user: UserModel = Depends(current_user_online),
):
    opponent_invites = GAME_INVITES[opponent_id]
    if user.user_id not in opponent_invites:
        raise HTTPException(404, "Invite not found")

    opponent_invites.pop(user.user_id)
    await Notifier.game_invite_rejected(opponent_id, user)

    return {"message": "Game invite rejected"}
