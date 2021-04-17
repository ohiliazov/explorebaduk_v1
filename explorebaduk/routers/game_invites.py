import random
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException

from ..crud import create_game, create_game_player
from ..dependencies import current_user_online
from ..models import UserModel
from ..schemas import Color, GameRequest
from ..shared import GameRequests

router = APIRouter(prefix="/game-invites", tags=["game-invites"])


@router.get("", response_model=Dict[int, GameRequest])
async def list_direct_invites(user: UserModel = Depends(current_user_online)):
    return GameRequests.get_direct_invites(user.user_id)


@router.post("/{opponent_id}", response_model=GameRequest)
async def create_game_invite(
    opponent_id: int, game: GameRequest, user: UserModel = Depends(current_user_online)
):
    if opponent_id in GameRequests.get_direct_invites(user.user_id):
        raise HTTPException(400, "Direct invite to this user already exists")

    await GameRequests.create_direct_invite(opponent_id, user, game)
    return game


@router.delete("/{opponent_id}")
async def cancel_game_invite(
    opponent_id: int, user: UserModel = Depends(current_user_online)
):
    if opponent_id not in GameRequests.get_direct_invites(user.user_id):
        raise HTTPException(404, "Direct invite not found")

    await GameRequests.remove_direct_invite(opponent_id, user)
    return {"message": "Direct invite cancelled"}


@router.post("/{opponent_id}/accept")
async def accept_game_invite(
    opponent_id: int,
    user: UserModel = Depends(current_user_online),
):
    if not (game_setup := GameRequests.get_direct_invite(opponent_id, user.user_id)):
        raise HTTPException(404, "Invite not found")

    # create game model here
    color = game_setup.game_settings.color

    if color is Color.NIGIRI:
        color = random.choice([Color.BLACK, Color.WHITE])

    if color is Color.BLACK:
        black_id, white_id = opponent_id, user.user_id
    else:
        black_id, white_id = user.user_id, opponent_id

    game_id = create_game(
        name=game_setup.name,
        rules=game_setup.rules,
        game_type=game_setup.game_type,
        category=game_setup.category,
        board_size=game_setup.board_size,
        handicap=game_setup.game_settings.handicap,
        komi=game_setup.game_settings.komi,
        time_settings=game_setup.time_settings.dict(),
    )

    create_game_player(
        game_id=game_id,
        user_id=black_id,
        color=Color.BLACK,
        time_left=game_setup.time_settings.get_total_time(),
    )
    create_game_player(
        game_id=game_id,
        user_id=white_id,
        color=Color.WHITE,
        time_left=game_setup.time_settings.get_total_time(),
    )
    await GameRequests.accept_direct_invite(opponent_id, user)
    return {"message": "Game invite accepted", "game_id": game_id}


@router.delete("/{opponent_id}/accept")
async def reject_game_invite(
    opponent_id: int,
    user: UserModel = Depends(current_user_online),
):
    if user.user_id not in GameRequests.get_direct_invites(opponent_id):
        raise HTTPException(404, "Invite not found")

    await GameRequests.reject_direct_invite(opponent_id, user)
    return {"message": "Game invite rejected"}
