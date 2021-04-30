from enum import Enum
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, root_validator, validator
from pydantic.types import ConstrainedFloat, ConstrainedInt, PositiveInt

from explorebaduk.constants import GameType, TimeSystem


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class CreatorColor(str, Enum):
    AUTO = "auto"
    NIGIRI = "nigiri"
    BLACK = "black"
    WHITE = "white"

    def is_random(self):
        return self.value is self.NIGIRI


class PlayerColor(str, Enum):
    BLACK = "black"
    WHITE = "white"


class GameSpeed(str, Enum):
    BLITZ = "blitz"
    LIVE = "live"
    CORRESPONDENCE = "correspondence"


class Rules(str, Enum):
    JAPANESE = "japanese"
    CHINESE = "chinese"


DEFAULT_KOMI = {
    Rules.JAPANESE.value: 6.5,
    Rules.CHINESE.value: 7.5,
}

Handicap = Literal[0, 2, 3, 4, 5, 6, 7, 8, 9]


class NonNegativeInt(ConstrainedInt):
    ge = 0


class NonNegativeFloat(ConstrainedFloat):
    ge = 0


class BoardSize(ConstrainedInt):
    ge = 5
    le = 52


class Komi(ConstrainedFloat):
    multiple_of = 0.5


class NewUserRating(ConstrainedInt):
    ge = 10
    le = 2300


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    username: str
    country: str
    avatar: str = None


class UserCreate(UserBase):
    rating: NewUserRating = 10
    puzzle_rating: NewUserRating = 10
    password: str
    password2: str

    @validator("password2")
    def passwords_match(cls, v, values, **kwargs):
        assert v == values["password"], "passwords do not match"
        return v

    @validator("username")
    def username_alphanumeric(cls, v: str):
        assert v.isalnum(), "username must be alphanumeric"
        return v

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "johndoe@explorebaduk.com",
                "username": "johndoe",
                "country": "Ukraine",
                "rating": 2100,
                "puzzle_rating": None,
                "avatar": "my-uploaded-avatar.jpg",
                "password": "mySuperStr0ngp4ssw0rd",
                "password2": "mySuperStr0ngp4ssw0rd",
            },
        }


class User(UserBase):
    user_id: int
    rating: float
    puzzle_rating: float

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "user_id": 123,
                "first_name": "John",
                "last_name": "Doe",
                "email": "johndoe@explorebaduk.com",
                "username": "johndoe",
                "country": "Ukraine",
                "rating": 1992.532,
                "puzzle_rating": 1605.321,
                "avatar": "avatar.jpg",
            },
        }


class FriendList(BaseModel):
    mutual: List[int]
    following: List[int]
    followers: List[int]
    blacklist: List[int]

    class Config:
        schema_extra = {
            "example": {
                "following": [132, 242, 312],
                "followers": [412, 523],
                "mutual": [777],
                "blacklist": [666],
            },
        }


class Unlimited(BaseModel):
    time_system: Literal[TimeSystem.UNLIMITED]

    def get_total_time(self):
        return None

    class Config:
        schema_extra = {"example": {"time_system": TimeSystem.UNLIMITED}}


class Absolute(BaseModel):
    time_system: Literal[TimeSystem.ABSOLUTE]
    main_time: PositiveInt

    def get_total_time(self):
        return self.main_time

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

    def get_total_time(self):
        return self.main_time + self.overtime * self.periods

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

    def get_total_time(self):
        return self.main_time + self.overtime

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

    def get_total_time(self):
        return self.main_time

    class Config:
        schema_extra = {
            "example": {
                "time_system": TimeSystem.CANADIAN,
                "main_time": 600,
                "bonus": 10,
                "max_time": 1200,
            },
        }


class GameSetupBase(BaseModel):
    name: str
    board_size: BoardSize = 19
    game_type: GameType
    category: GameSpeed
    is_private: bool = False
    rules: Rules
    time_settings: Union[Unlimited, Absolute, Byoyomi, Canadian, Fischer]

    class Config:
        schema_extra = {
            "example": {
                "name": "My first game",
                "board_size": 19,
                "game_type": GameType.RANKED,
                "category": GameSpeed.LIVE,
                "is_private": False,
                "rules": Rules.JAPANESE,
                "time_settings": Byoyomi.Config.schema_extra["example"],
            },
        }


class GameRestrictions(BaseModel):
    min_rating: NonNegativeInt = 0
    max_rating: NonNegativeInt = 3000
    min_handicap: Handicap = 0
    max_handicap: Handicap = 9

    class Config:
        schema_extra = {
            "example": {
                "min_rating": 1900,
                "max_rating": 2400,
                "min_handicap": 0,
                "max_handicap": 3,
            },
        }


class OpenGame(GameSetupBase):
    restrictions: Optional[GameRestrictions]

    class Config:
        schema_extra = {
            "example": {
                **GameSetupBase.Config.schema_extra["example"],
                "restrictions": GameRestrictions.Config.schema_extra["example"],
            },
        }


class GameSettings(BaseModel):
    color: CreatorColor
    handicap: Handicap
    komi: Komi

    @root_validator
    def validate_game_settings(cls, values: dict):
        if values["color"] is CreatorColor.NIGIRI:
            values["handicap"] = 0
        return values

    class Config:
        schema_extra = {"example": {"color": "black", "handicap": 3, "komi": 0.5}}


class GameRequest(GameSetupBase):
    game_settings: GameSettings

    class Config:
        schema_extra = {
            "example": {
                **GameSetupBase.Config.schema_extra["example"],
                "game_settings": GameSettings.Config.schema_extra["example"],
            },
        }


class GameCreate(BaseModel):
    name: str
    private: bool
    ranked: bool
    board_size: BoardSize
    rules: Rules
    speed: GameSpeed
    time_control: Union[Unlimited, Absolute, Byoyomi, Canadian, Fischer]
    handicap: Handicap = None
    komi: Komi = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "The Battlefield",
                "private": False,
                "ranked": True,
                "board_size": 19,
                "rules": Rules.JAPANESE.value,
                "speed": GameSpeed.LIVE.value,
                "time_control": Byoyomi.Config.schema_extra["example"],
                "handicap": None,
                "komi": None,
            },
        }


class ChallengeCreate(BaseModel):
    game: GameCreate
    opponent_id: int = None
    creator_color: CreatorColor
    min_rating: int = None
    max_rating: int = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "game": GameCreate.Config.schema_extra["example"],
                "opponent_id": None,
                "creator_color": CreatorColor.NIGIRI.value,
                "min_rating": 1200,
                "max_rating": 2400,
            },
        }


class GamePlayer(BaseModel):
    game_id: int
    user_id: int
    color: PlayerColor
    time_left: float


class Game(GameCreate):
    game_id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "game_id": 654,
                "name": "The Battlefield",
                "private": False,
                "ranked": True,
                "board_size": 19,
                "rules": Rules.JAPANESE.value,
                "speed": GameSpeed.LIVE.value,
                "time_control": Byoyomi.Config.schema_extra["example"],
                "handicap": 3,
                "komi": 0.5,
            },
        }


class Challenge(ChallengeCreate):
    game: Game
    challenge_id: int = None
    creator_id: int = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "challenge_id": 1234,
                "creator_id": 23,
                "game": GameCreate.Config.schema_extra["example"],
                "opponent_id": None,
                "creator_color": CreatorColor.NIGIRI.value,
                "min_rating": 1200,
                "max_rating": 2400,
            },
        }
