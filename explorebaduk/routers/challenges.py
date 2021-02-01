from fastapi.routing import APIRouter

from explorebaduk.broadcast import broadcast
from explorebaduk.schemas import Challenge

router = APIRouter(
    prefix="/api",
)


@router.post("/challenges")
async def create_challenge(challenge: Challenge):
    await broadcast.publish("main", {"event": "challenges.add", "data": challenge.dict()})
    return challenge
