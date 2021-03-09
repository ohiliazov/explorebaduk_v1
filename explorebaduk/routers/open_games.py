from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import current_user_online
from ..helpers import Notifier
from ..models import UserModel
from ..schemas import GameSettingsIn, OpenGame
from ..shared import OPEN_GAME_REQUESTS, OPEN_GAMES

router = APIRouter()


@router.post("/open-games", response_model=OpenGame)
async def create_open_game(
    game: OpenGame,
    user: UserModel = Depends(current_user_online),
):
    if user.user_id in OPEN_GAMES:
        raise HTTPException(400, "Open game invite already exists")

    OPEN_GAMES[user.user_id] = game.dict()
    await Notifier.open_game_created(user, game)

    return game


@router.delete("/open-games/user_id")
async def cancel_game_creation(
    user_id: int, user: UserModel = Depends(current_user_online)
):
    if user.user_id != user_id:
        raise HTTPException(403, "Forbidden")

    if user_id not in OPEN_GAMES:
        raise HTTPException(404, "Game not found")

    OPEN_GAMES.pop(user_id)
    await Notifier.open_game_cancelled(user)

    return {"message": "Game creation cancelled"}


@router.post("/open-games/{user_id}/request")
async def request_open_game(
    user_id: int,
    settings: GameSettingsIn,
    user: UserModel = Depends(current_user_online),
):
    if user_id not in OPEN_GAMES:
        raise HTTPException(404, "Game not found")

    OPEN_GAME_REQUESTS[user_id][user.user_id] = settings
    await Notifier.open_game_requested(user_id, user, settings)

    return {"message": "Game requested"}


@router.post("/open-games/{user_id}/request/{opponent_id}")
async def accept_open_game(
    user_id: int, opponent_id: int, user: UserModel = Depends(current_user_online)
):
    if user.user_id != user_id:
        raise HTTPException(403, "Forbidden")

    if user_id not in OPEN_GAMES:
        raise HTTPException(404, "Open game not created")

    if opponent_id not in OPEN_GAME_REQUESTS[user_id]:
        raise HTTPException(404, "User not requested the game")

    # create game model here
    await Notifier.open_game_accepted(opponent_id, user)

    return {"message": "Game accepted"}


@router.delete("/open-games/{user_id}/request/{opponent_id}")
async def reject_open_game(
    user_id: int, opponent_id: int, user: UserModel = Depends(current_user_online)
):
    if user.user_id != user_id:
        raise HTTPException(403, "Forbidden")

    if user_id not in OPEN_GAMES:
        raise HTTPException(404, "Open game not created")

    if opponent_id not in OPEN_GAME_REQUESTS[user_id]:
        raise HTTPException(404, "User not requested the game")

    OPEN_GAME_REQUESTS[user_id].pop(opponent_id)
    await Notifier.open_game_rejected(opponent_id, user)

    return {"message": "Game rejected"}
