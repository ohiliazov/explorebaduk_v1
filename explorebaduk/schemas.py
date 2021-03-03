from typing import Literal, Optional, Set, Union

from pydantic import BaseModel
from pydantic.types import ConstrainedFloat, ConstrainedInt, PositiveInt

from explorebaduk.constants import Color, GameCategory, RuleSet, TimeSystem


class NonNegativeInt(ConstrainedInt):
    ge = 0


class NonNegativeFloat(ConstrainedFloat):
    ge = 0


class BoardSize(ConstrainedInt):
    ge = 5
    le = 52


class Komi(ConstrainedFloat):
    multiple_of = 0.5


class PlayerOut(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: str
    username: str
    rating: NonNegativeFloat = 10
    puzzle_rating: NonNegativeFloat = 0
    avatar: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "user_id": 123,
                "first_name": "John",
                "last_name": "Doe",
                "email": "johndoe@explorebaduk.com",
                "username": "johndoe",
                "rating": 1992.532,
                "puzzle_rating": 1605.321,
                "avatar": "avatar.jpg",
            },
        }


class FriendListOut(BaseModel):
    friends: Set[int]
    pending: Optional[Set[int]]
    waiting: Optional[Set[int]]

    class Config:
        schema_extra = {
            "example": {
                "friends": [132, 242, 312],
                "pending": [412, 523],
                "waiting": [676],
            },
        }


class Unlimited(BaseModel):
    time_system: Literal[TimeSystem.UNLIMITED]

    class Config:
        schema_extra = {"example": {"time_system": TimeSystem.UNLIMITED}}


class Absolute(BaseModel):
    time_system: Literal[TimeSystem.ABSOLUTE]
    main_time: PositiveInt

    class Config:
        schema_extra = {
            "example": {
                "time_system": TimeSystem.ABSOLUTE,
                "main_time": 3600,
            },
        }


class Byoyomi(BaseModel):
    time_system: Literal[TimeSystem.BYOYOMI]
    main_time: NonNegativeInt
    overtime: PositiveInt
    periods: PositiveInt

    class Config:
        schema_extra = {
            "example": {
                "time_system": TimeSystem.BYOYOMI,
                "main_time": 3600,
                "overtime": 30,
                "periods": 5,
            },
        }


class Canadian(BaseModel):
    time_system: Literal[TimeSystem.CANADIAN]
    main_time: NonNegativeInt
    overtime: PositiveInt
    stones: PositiveInt

    class Config:
        schema_extra = {
            "example": {
                "time_system": TimeSystem.CANADIAN,
                "main_time": 3600,
                "overtime": 300,
                "stones": 20,
            },
        }


class Fischer(BaseModel):
    time_system: Literal[TimeSystem.FISCHER]
    main_time: PositiveInt
    bonus: PositiveInt
    max_time: PositiveInt

    class Config:
        schema_extra = {
            "example": {
                "time_system": TimeSystem.CANADIAN,
                "main_time": 600,
                "bonus": 10,
                "max_time": 1200,
            },
        }


class Game(BaseModel):
    name: str
    board_size: BoardSize = 19
    is_ranked: bool = False
    is_private: bool = False
    category: GameCategory
    rules: RuleSet
    time_settings: Union[Unlimited, Absolute, Byoyomi, Canadian, Fischer]

    class Config:
        schema_extra = {
            "example": {
                "name": "My first game",
                "board_size": 19,
                "is_ranked": False,
                "is_private": False,
                "category": GameCategory.REAL_TIME,
                "rules": RuleSet.JAPANESE,
                "time_settings": Byoyomi.Config.schema_extra["example"],
            },
        }


class GameRestrictions(BaseModel):
    min_rating: NonNegativeInt = 0
    max_rating: NonNegativeInt = 3000
    min_handicap: Literal[0, 2, 3, 4, 5, 6, 7, 8, 9] = 0
    max_handicap: Literal[0, 2, 3, 4, 5, 6, 7, 8, 9] = 9

    class Config:
        schema_extra = {
            "example": {
                "min_rating": 1900,
                "max_rating": 2400,
                "min_handicap": 0,
                "max_handicap": 3,
            },
        }


class OpenGame(Game):
    restrictions: GameRestrictions

    class Config:
        schema_extra = {
            "example": {
                "name": "My first game",
                "board_size": 19,
                "is_ranked": False,
                "is_private": False,
                "category": GameCategory.REAL_TIME,
                "rules": RuleSet.JAPANESE,
                "time_settings": Canadian.Config.schema_extra["example"],
                "restrictions": GameRestrictions.Config.schema_extra["example"],
            },
        }


class Nigiri(BaseModel):
    color: Literal[Color.NIGIRI]
    handicap: Literal[0]
    komi: Komi

    class Config:
        schema_extra = {"example": {"color": "nigiri", "handicap": 0, "komi": 6.5}}


class DefinedColor(BaseModel):
    color: Literal[Color.BLACK, Color.WHITE]
    handicap: Literal[0, 2, 3, 4, 5, 6, 7, 8, 9]
    komi: Komi

    class Config:
        schema_extra = {"example": {"color": "black", "handicap": 3, "komi": 0.5}}


class DirectGame(Game):
    game_settings: Union[Nigiri, DefinedColor]

    class Config:
        schema_extra = {
            "example": {
                "name": "My first game",
                "board_size": 19,
                "is_ranked": False,
                "is_private": False,
                "category": GameCategory.REAL_TIME,
                "rules": RuleSet.JAPANESE,
                "time_settings": Canadian.Config.schema_extra["example"],
                "game_settings": DefinedColor.Config.schema_extra["example"],
            },
        }
