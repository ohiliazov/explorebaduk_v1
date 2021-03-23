from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import current_user, current_user_online
from ..models import UserModel
from ..schemas import GameSettings, OpenGame
from ..shared import GameRequests

router = APIRouter(prefix="/open-games", tags=["open-games"])


@router.get("", response_model=List[OpenGame], dependencies=[Depends(current_user)])
async def list_open_games():
    return GameRequests.list_open_games()


@router.post("", response_model=OpenGame)
async def create_open_game(
    game: OpenGame,
    user: UserModel = Depends(current_user_online),
):
    if GameRequests.get_open_game(user.user_id):
        raise HTTPException(400, "Open game invite already exists")

    await GameRequests.set_open_game(user, game)
    return game


@router.delete("")
async def cancel_game_creation(user: UserModel = Depends(current_user_online)):
    try:
        await GameRequests.remove_open_game(user)
    except KeyError:
        raise HTTPException(404, "Game not found")
    return {"message": "Open game cancelled"}


@router.get("/{user_id}", response_model=OpenGame, dependencies=[Depends(current_user)])
async def get_open_game(user_id: int):
    if game := GameRequests.get_open_game(user_id):
        return game
    raise HTTPException(404, "Open game not found")


@router.post("/{user_id}/request")
async def request_open_game(
    user_id: int,
    settings: GameSettings,
    user: UserModel = Depends(current_user_online),
):
    if not GameRequests.get_open_game(user_id):
        raise HTTPException(404, "Game not found")

    await GameRequests.request_open_game(user_id, user, settings)
    return {"message": "Game requested"}


@router.post("/{user_id}/request/{opponent_id}")
async def accept_open_game(user_id: int, opponent_id: int, user: UserModel = Depends(current_user_online)):
    if user.user_id != user_id:
        raise HTTPException(403, "Forbidden")

    if not GameRequests.get_open_game(user_id):
        raise HTTPException(404, "Open game not created")

    if not GameRequests.get_open_game_request(user_id):
        raise HTTPException(404, "User not requested the game")

    # create game model here
    await GameRequests.accept_open_game(user, opponent_id)
    return {"message": "Game accepted"}


@router.delete("/{user_id}/request/{opponent_id}")
async def reject_open_game(user_id: int, opponent_id: int, user: UserModel = Depends(current_user_online)):
    if user.user_id != user_id:
        raise HTTPException(403, "Forbidden")

    if not GameRequests.get_open_game(user_id):
        raise HTTPException(404, "Open game not created")

    if not GameRequests.get_open_game_request(user_id):
        raise HTTPException(404, "User not requested the game")

    await GameRequests.reject_open_game(user, opponent_id)
    return {"message": "Game rejected"}
