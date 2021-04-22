from fastapi import APIRouter, Depends, HTTPException

from explorebaduk.messages import Notifier

from ..crud import DatabaseHandler
from ..dependencies import current_user
from ..models import UserModel
from ..schemas import Challenge

router = APIRouter(tags=["challenges"])


@router.post("/challenges")
async def create_challenge(
    challenge: Challenge, user: UserModel = Depends(current_user)
):
    with DatabaseHandler() as db:
        game = db.create_game(challenge.game)
        challenge = db.create_challenge(challenge, game, user.user_id)

        await Notifier.challenge_created(challenge.asdict())

    return {
        "game_id": game.game_id,
        "challenge_id": challenge.challenge_id,
    }


@router.post("/players/{user_id}/challenge")
async def create_direct_challenge(
    user_id: int, challenge: Challenge, user: UserModel = Depends(current_user)
):
    with DatabaseHandler() as db:
        game = db.create_game(challenge.game)
        challenge = db.create_challenge(challenge, game, user.user_id, user_id)

        await Notifier.direct_challenge_created(challenge.asdict())

    return {
        "game_id": game.game_id,
        "challenge_id": challenge.challenge_id,
    }


@router.delete("/challenges/{challenge_id}")
async def cancel_challenge(challenge_id: int, user: UserModel = Depends(current_user)):
    with DatabaseHandler() as db:
        challenge = db.get_challenge_by_id(challenge_id)

        if not challenge:
            raise HTTPException(404, "Challenge not found")

        if challenge.creator_id != user.user_id:
            raise HTTPException(403, "Cannot remove challenge")

        db.session.delete(challenge)

        if challenge.opponent_id:
            await Notifier.direct_challenge_cancelled(challenge.asdict())
        else:
            await Notifier.challenge_cancelled(challenge.asdict())

    return {"message": "Challenge removed"}


@router.delete("/challenges/{challenge_id}/accept")
async def accept_challenge(challenge_id: int, user: UserModel = Depends(current_user)):
    with DatabaseHandler() as db:
        challenge = db.get_challenge_by_id(challenge_id)

        if not challenge:
            raise HTTPException(404, "Challenge not found")

        if challenge.opponent_id and challenge.opponent_id != user.user_id:
            raise HTTPException(403, "Cannot accept this challenge")

        game = db.start_game(challenge, user.user_id)

        await Notifier.game_started(game.game_id, challenge.creator_id, user.user_id)
        await Notifier.challenge_cancelled(game.game_id)

    return {"game_id": game.game_id}
