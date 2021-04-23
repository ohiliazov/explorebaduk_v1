from fastapi import APIRouter, Depends, HTTPException

from explorebaduk.crud import DatabaseHandler
from explorebaduk.dependencies import current_user, get_db_session
from explorebaduk.messages import Notifier
from explorebaduk.models import UserModel
from explorebaduk.schemas import Challenge

router = APIRouter(tags=["challenges"])


@router.get("/challenges")
async def list_challenges(
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(get_db_session),
):
    return db.list_challenges()


@router.post("/challenges", response_model=Challenge)
async def create_challenge(
    challenge: Challenge,
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(get_db_session),
):
    game = db.create_game(challenge.game)
    challenge = db.create_challenge(challenge, game, user.user_id)

    await Notifier.challenge_created(challenge)

    return challenge


@router.post("/players/{user_id}/challenge")
async def create_direct_challenge(
    user_id: int,
    challenge: Challenge,
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(get_db_session),
):
    game = db.create_game(challenge.game)
    challenge = db.create_challenge(challenge, game, user.user_id, user_id)

    await Notifier.direct_challenge_created(challenge)

    return {
        "game_id": game.game_id,
        "challenge_id": challenge.challenge_id,
    }


@router.delete("/challenges/{challenge_id}")
async def cancel_challenge(
    challenge_id: int,
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(get_db_session),
):
    challenge = db.get_challenge_by_id(challenge_id)

    if not challenge:
        raise HTTPException(404, "Challenge not found")

    if challenge.creator_id != user.user_id:
        raise HTTPException(403, "Cannot remove challenge")

    db.session.delete(challenge)
    db.session.flush()

    await Notifier.challenge_cancelled(challenge)

    return {"message": "Challenge removed"}


@router.post("/challenges/{challenge_id}/accept")
async def accept_challenge(
    challenge_id: int,
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(get_db_session),
):
    challenge = db.get_challenge_by_id(challenge_id)

    if not challenge:
        raise HTTPException(404, "Challenge not found")

    if challenge.opponent_id and challenge.opponent_id != user.user_id:
        raise HTTPException(403, "Cannot accept this challenge")

    game = db.start_game(challenge, user.user_id)
    await Notifier.challenge_accepted(game.game_id)

    return {"game_id": game.game_id}


@router.post("/challenges/{challenge_id}/reject")
async def refuse_challenge(
    challenge_id: int,
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(get_db_session),
):
    challenge = db.get_challenge_by_id(challenge_id)

    if not challenge:
        raise HTTPException(404, "Challenge not found")

    if not challenge.opponent_id or challenge.opponent_id != user.user_id:
        raise HTTPException(403, "Cannot reject this challenge")

    db.session.delete(challenge.game)
    db.session.delete(challenge)
    db.session.flush()

    await Notifier.challenge_rejected(challenge)

    return {"message": "Challenge rejected"}
