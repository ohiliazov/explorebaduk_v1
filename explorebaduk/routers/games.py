from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import current_user_online
from ..helpers import Notifier
from ..models import UserModel
from ..schemas import DirectGame, OpenGame
from ..shared import GAME_INVITES, OPEN_GAMES

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


@router.post("/open-games/{opponent_id}/accept")
async def accept_open_game(
    opponent_id: int,
    user: UserModel = Depends(current_user_online),
):
    if opponent_id not in OPEN_GAMES:
        raise HTTPException(404, "Game not found")

    # create game model here
    await Notifier.open_game_accepted(opponent_id, user)

    return {"message": "Game accepted"}


@router.post("/game-invites/{opponent_id}", response_model=DirectGame)
async def create_game_invite(
    opponent_id: int, game: DirectGame, user: UserModel = Depends(current_user_online)
):
    direct_invites = GAME_INVITES[user.user_id]

    if opponent_id in direct_invites:
        raise HTTPException(400, "Direct invite to this user already exists")

    direct_invites[opponent_id] = game.dict()
    await Notifier.direct_invite_created(opponent_id, user, game)

    return game


@router.delete("/game-invites/{opponent_id}")
async def cancel_game_invite(
    opponent_id: int, user: UserModel = Depends(current_user_online)
):
    direct_invites = GAME_INVITES[user.user_id]

    if opponent_id not in direct_invites:
        raise HTTPException(404, "Direct invite not found")

    direct_invites.pop(opponent_id)
    await Notifier.direct_invite_cancelled(opponent_id, user)

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
    await Notifier.open_game_accepted(opponent_id, user)

    return {"message": "Game accepted"}
