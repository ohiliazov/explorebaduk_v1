from fastapi import APIRouter, Depends, HTTPException

from explorebaduk.crud import DatabaseHandler
from explorebaduk.dependencies import current_user, get_db_session
from explorebaduk.messages import Notifier
from explorebaduk.models import UserModel
from explorebaduk.schemas import Challenge, ChallengeCreate, Game

router = APIRouter(tags=["challenges"])


@router.get("/challenges")
async def list_challenges(
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(get_db_session),
):
    return db.list_challenges()


@router.post("/challenges", response_model=Challenge)
async def create_challenge(
    challenge: ChallengeCreate,
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(get_db_session),
):
    challenge = db.create_challenge(challenge, user.user_id)

    if challenge.opponent_id:
        await Notifier.direct_challenge_created(challenge)
    else:
        await Notifier.challenge_created(challenge)

    return challenge


@router.post("/challenges/{challenge_id}/accept", response_model=Game)
async def accept_challenge(
    challenge_id: int,
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(get_db_session),
):
    challenge = db.get_challenge_by_id(challenge_id)

    if not challenge:
        raise HTTPException(404, "Challenge not found")

    if user.user_id == challenge.creator_id:
        raise HTTPException(403, "You cannot accept your own challenge")

    if challenge.opponent_id and challenge.opponent_id != user.user_id:
        raise HTTPException(403, "Cannot accept challenge to another user")

    game = db.start_game(challenge, user.user_id)

    if challenge.opponent_id:
        await Notifier.direct_challenge_accepted(challenge)
    else:
        await Notifier.challenge_accepted(challenge)

    return game


@router.delete("/challenges/{challenge_id}")
async def cancel_challenge(
    challenge_id: int,
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(get_db_session),
):
    challenge = db.get_challenge_by_id(challenge_id)

    if not challenge:
        raise HTTPException(404, "Challenge not found")

    if user.user_id != challenge.creator_id:
        raise HTTPException(403, "Cannot remove challenge")

    db.session.delete(challenge)
    db.session.flush()

    if challenge.opponent_id:
        await Notifier.direct_challenge_cancelled(challenge)
    else:
        await Notifier.challenge_cancelled(challenge)

    return {"message": "Challenge removed"}


@router.post("/challenges/{challenge_id}/reject")
async def reject_challenge(
    challenge_id: int,
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(get_db_session),
):
    challenge = db.get_challenge_by_id(challenge_id)

    if not challenge:
        raise HTTPException(404, "Challenge not found")

    if user.user_id != challenge.opponent_id:
        raise HTTPException(403, "Cannot reject this challenge")

    db.session.delete(challenge)
    db.session.flush()

    await Notifier.direct_challenge_rejected(challenge)

    return {"message": "Challenge removed"}
