from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import current_user_online
from ..helpers import Notifier
from ..models import UserModel
from ..schemas import GameSettingsIn, OpenGame
from ..shared import OPEN_GAME_REQUESTS, OPEN_GAMES

router = APIRouter()


@router.post("/open-games", response_model=OpenGame)
async def create_open_game(
    game: OpenGame, user: UserModel = Depends(current_user_online)
):
    if user.user_id in OPEN_GAMES:
        raise HTTPException(400, "Open game invite already exists")

    OPEN_GAMES[user.user_id] = game.dict()
    await Notifier.open_game_created(user, game)

    return game


@router.delete("/open-games")
async def cancel_game_creation(user: UserModel = Depends(current_user_online)):
    if user.user_id not in OPEN_GAMES:
        raise HTTPException(404, "Game not found")

    OPEN_GAMES.pop(user.user_id)
    await Notifier.open_game_cancelled(user)

    return {"message": "Game creation cancelled"}


@router.post("/open-games/request/{opponent_id}")
async def request_open_game(
    opponent_id: int,
    settings: GameSettingsIn,
    user: UserModel = Depends(current_user_online),
):
    if opponent_id not in OPEN_GAMES:
        raise HTTPException(404, "Game not found")

    OPEN_GAME_REQUESTS[opponent_id][user.user_id] = settings
    await Notifier.open_game_requested(opponent_id, user, settings)

    return {"message": "Game requested"}


@router.post("/open-games/accept/{opponent_id}")
async def accept_open_game(
    opponent_id: int, user: UserModel = Depends(current_user_online)
):
    if user.user_id not in OPEN_GAMES:
        raise HTTPException(404, "Open game not created")

    if opponent_id not in OPEN_GAME_REQUESTS[user.user_id]:
        raise HTTPException(404, "User not requested the game")

    # create game model here
    await Notifier.open_game_accepted(opponent_id, user)

    return {"message": "Game accepted"}


@router.post("/open-games/reject/{opponent_id}")
async def reject_open_game(
    opponent_id: int, user: UserModel = Depends(current_user_online)
):
    if user.user_id not in OPEN_GAMES:
        raise HTTPException(404, "Open game not created")

    if opponent_id not in OPEN_GAME_REQUESTS[user.user_id]:
        raise HTTPException(404, "User not requested the game")

    OPEN_GAME_REQUESTS[user.user_id].pop(opponent_id)
    await Notifier.open_game_rejected(opponent_id, user)

    return {"message": "Game rejected"}
