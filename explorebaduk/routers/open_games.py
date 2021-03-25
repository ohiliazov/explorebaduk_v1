from typing import Dict

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import current_user_online
from ..models import UserModel
from ..schemas import GameSettings, OpenGame
from ..shared import GameRequests

router = APIRouter(prefix="/open-games", tags=["open-games"])


@router.get("", response_model=Dict[int, OpenGame])
async def list_open_games():
    return GameRequests.open_games


@router.post("", response_model=OpenGame)
async def create_open_game(game: OpenGame, user: UserModel = Depends(current_user_online)):
    if GameRequests.get_open_game(user.user_id):
        raise HTTPException(400, "Open game invite already exists")

    await GameRequests.set_open_game(user, game)
    return game


@router.delete("")
async def cancel_open_game(user: UserModel = Depends(current_user_online)):
    await GameRequests.remove_open_game(user)
    return {"message": "Open game cancelled"}


@router.get("/requests", response_model=Dict[int, GameSettings])
async def list_open_game_requests(user: UserModel = Depends(current_user_online)):
    return GameRequests.get_open_game_requests(user.user_id)


@router.post("/{to_user_id}")
async def create_open_game_request(
    to_user_id: int,
    settings: GameSettings,
    user: UserModel = Depends(current_user_online),
):
    if not GameRequests.get_open_game(to_user_id):
        raise HTTPException(404, "Game not found")

    await GameRequests.create_open_game_request(to_user_id, user, settings)
    return {"message": "Game requested"}


@router.post("/{to_user_id}")
async def cancel_open_game_request(to_user_id: int, user: UserModel = Depends(current_user_online)):
    if not GameRequests.get_open_game(to_user_id):
        raise HTTPException(404, "Game not found")

    await GameRequests.remove_open_game_request(to_user_id, user)
    return {"message": "Game requested"}


@router.post("/{from_user_id}/accept")
async def accept_open_game(from_user_id: int, user: UserModel = Depends(current_user_online)):
    if from_user_id not in GameRequests.get_open_game_requests(user.user_id):
        raise HTTPException(404, "User not requested the game")

    # create game model here
    await GameRequests.accept_open_game_request(user, from_user_id)
    return {"message": "Game accepted"}


@router.delete("/{from_user_id}/accept")
async def reject_open_game(from_user_id: int, user: UserModel = Depends(current_user_online)):
    if from_user_id not in GameRequests.get_open_game_requests(user.user_id):
        raise HTTPException(404, "User not requested the game")

    await GameRequests.reject_open_game_request(user, from_user_id)
    return {"message": "Game rejected"}
