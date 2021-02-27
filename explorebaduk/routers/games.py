from fastapi import APIRouter, Depends, HTTPException

from explorebaduk.broadcast import broadcast
from explorebaduk.dependencies import get_current_user
from explorebaduk.messages import (
    DirectInviteCancelledMessage,
    DirectInviteCreatedMessage,
    OpenGameCancelledMessage,
    OpenGameCreatedMessage,
)
from explorebaduk.models import UserModel
from explorebaduk.schemas import OpenGame
from explorebaduk.shared import DIRECT_INVITES, OPEN_GAMES

router = APIRouter(prefix="/api")


async def create_open_game(game: OpenGame, user: UserModel):
    if user.user_id in OPEN_GAMES:
        OPEN_GAMES.pop(user.user_id)
        await broadcast.publish("main", OpenGameCancelledMessage(user).json())

    OPEN_GAMES[user.user_id] = game.dict()
    await broadcast.publish("main", OpenGameCreatedMessage(user, game.dict()).json())

    return game


async def send_direct_game_invite(game: OpenGame, user: UserModel):
    opponent_id = game.opponent_id
    opponent_game_invites = DIRECT_INVITES[opponent_id]

    if user.user_id in opponent_game_invites:
        opponent_game_invites.pop(user.user_id)
        await broadcast.publish(
            f"user__{opponent_id}",
            DirectInviteCancelledMessage(user).json(),
        )

    opponent_game_invites[user.user_id] = game.dict()
    await broadcast.publish(
        f"user__{opponent_id}",
        DirectInviteCreatedMessage(user, game.dict()).json(),
    )

    return game


@router.post("/games", response_model=OpenGame)
async def create_game(game: OpenGame, user: UserModel = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not game.opponent_id:
        return await create_open_game(game, user)
    else:
        return await send_direct_game_invite(game, user)


@router.post("/games/{user_id}", response_model=OpenGame)
async def get_game_info(user_id: int):
    if user_id not in OPEN_GAMES:
        raise HTTPException(404, {"message": "Game creation not found"})

    return OPEN_GAMES[user_id]


@router.delete("/games")
async def cancel_game_creation(user: UserModel = Depends(get_current_user)):
    if user.user_id not in OPEN_GAMES:
        raise HTTPException(404, {"message": "Game creation not found"})

    OPEN_GAMES.pop(user.user_id)
    await broadcast.publish("main", OpenGameCancelledMessage(user).json())

    return {"message": "Game creation cancelled"}
