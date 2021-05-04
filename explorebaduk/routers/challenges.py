from fastapi import APIRouter, Depends, HTTPException

from explorebaduk.database import DatabaseHandler
from explorebaduk.dependencies import current_user, db_handler
from explorebaduk.messages import Notifier
from explorebaduk.models import UserModel
from explorebaduk.schemas import (
    DEFAULT_KOMI,
    Challenge,
    ChallengeCreate,
    CreatorColor,
    Game,
    GamePlayer,
    PlayerColor,
)
from explorebaduk.utils import resolve_color

router = APIRouter(tags=["challenges"])


@router.get("/challenges")
async def list_open_challenges(
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(db_handler),
):
    return db.get_open_challenges()


@router.post("/challenges", response_model=Challenge)
async def create_challenge(
    challenge_data: ChallengeCreate,
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(db_handler),
):
    game = db.create_game(challenge_data.game)
    challenge = db.create_challenge(user, game, challenge_data)

    if challenge.opponent_id:
        await Notifier.direct_challenge_created(challenge)
    else:
        await Notifier.challenge_created(challenge)

    return challenge


@router.delete("/challenges/{challenge_id}")
async def cancel_challenge(
    challenge_id: int,
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(db_handler),
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


@router.post("/challenges/{challenge_id}/accept", response_model=Game)
async def accept_challenge(
    challenge_id: int,
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(db_handler),
):
    challenge = db.get_challenge_by_id(challenge_id)

    if not challenge:
        raise HTTPException(404, "Challenge not found")

    if user.user_id == challenge.creator_id:
        raise HTTPException(403, "You cannot accept your own challenge")

    if challenge.opponent_id and challenge.opponent_id != user.user_id:
        raise HTTPException(403, "Cannot accept challenge to another user")

    creator = db.get_user_by_id(challenge.creator_id)
    opponent = db.get_user_by_id(user.user_id)

    black, white = resolve_color(creator, opponent, challenge.creator_color)

    game = challenge.game

    if game.handicap is None:
        if challenge.creator_color is CreatorColor.AUTO:
            game.handicap = max(int((white.rating - black.rating) / 100), 0)
        else:
            game.handicap = 0

    if game.komi is None:
        if game.handicap > 0:
            game.komi = 0
        else:
            game.komi = DEFAULT_KOMI[game.rules]

    db.add(game)

    db.create_game_player(
        GamePlayer(
            game_id=game.game_id,
            user_id=black.user_id,
            color=PlayerColor.BLACK,
            time_left=game.initial_time,
        ),
    )

    db.create_game_player(
        GamePlayer(
            game_id=game.game_id,
            user_id=white.user_id,
            color=PlayerColor.WHITE,
            time_left=game.initial_time,
        ),
    )

    if challenge.opponent_id:
        await Notifier.direct_challenge_accepted(challenge)
    else:
        await Notifier.challenge_accepted(challenge)

    return game


@router.post("/challenges/{challenge_id}/reject")
async def reject_challenge(
    challenge_id: int,
    user: UserModel = Depends(current_user),
    db: DatabaseHandler = Depends(db_handler),
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
