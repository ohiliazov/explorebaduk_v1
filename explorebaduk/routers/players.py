from typing import List

from fastapi import APIRouter

from ..crud import DatabaseHandler
from ..schemas import PlayerOut
from ..shared import UsersOnline

router = APIRouter(prefix="/players", tags=["players"])


@router.get("", response_model=List[PlayerOut])
def list_players(q: str = None, only_online: bool = False):
    with DatabaseHandler() as db:
        players = db.get_users(q=q)

    if only_online:
        players = filter(UsersOnline.is_online, players)

    return [player.asdict() for player in players]


@router.get("/{player_id}", response_model=PlayerOut)
def get_player(player_id: int):
    with DatabaseHandler() as db:
        return db.get_user_by_id(player_id).asdict()
