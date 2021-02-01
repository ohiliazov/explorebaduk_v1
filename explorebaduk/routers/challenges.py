from fastapi.routing import APIRouter
from pydantic import BaseModel, validator

from explorebaduk.broadcast import broadcast
from explorebaduk.constants import (
    ALLOWED_GAME_TYPES,
    ALLOWED_RULES,
    ALLOWED_TIME_SYSTEMS,
)

router = APIRouter(
    prefix="/api",
)


class GameSetup(BaseModel):
    name: str
    type: str
    is_private: bool = False

    @validator("type")
    def validate_game_type(cls, value: str):
        assert value in ALLOWED_GAME_TYPES, f"Invalid game_type: {value}"


class RuleSet(BaseModel):
    rules: str
    board_size: int = 19

    @validator("rules")
    def validate_rules(cls, value: str):
        assert value in ALLOWED_RULES, f"Invalid rules: {value}"

    @validator("board_size")
    def validate_board_size(cls, value: int):
        assert 5 <= value <= 52, f"Invalid board_size: {value}"


class TimeSettings(BaseModel):
    time_system: str
    main_time: int = 0
    overtime: int = 0
    periods: int = 1
    stones: int = 1
    bonus: int = 0

    @validator("time_system")
    def validate_time_system(cls, value: str):
        assert value in ALLOWED_TIME_SYSTEMS, f"Invalid time_system: {value}"


class Challenge(BaseModel):
    game_setup: GameSetup
    rule_set: RuleSet
    time_settings: TimeSettings


@router.post("/challenges")
async def create_challenge(challenge: Challenge):
    await broadcast.publish("main", {"event": "challenges.add", "data": challenge.dict()})
    return challenge
