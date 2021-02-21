from fastapi import APIRouter, Depends, HTTPException

from explorebaduk.broadcast import broadcast
from explorebaduk.dependencies import get_current_user
from explorebaduk.messages import ChallengesAddMessage, ChallengesRemoveMessage
from explorebaduk.models import UserModel
from explorebaduk.schemas import Challenge
from explorebaduk.shared import CHALLENGES

router = APIRouter(
    prefix="/api",
)


@router.post("/challenges")
async def create_challenge(
    challenge: Challenge, user: UserModel = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if user.user_id in CHALLENGES:
        CHALLENGES.pop(user.user_id)
        await broadcast.publish("main", ChallengesRemoveMessage(user).json())

    CHALLENGES[user.user_id] = challenge
    await broadcast.publish("main", ChallengesAddMessage(user, challenge.dict()).json())

    return challenge
