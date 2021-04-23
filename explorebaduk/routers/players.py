from typing import List

from fastapi import APIRouter

from explorebaduk.crud import DatabaseHandler
from explorebaduk.managers import UsersManager
from explorebaduk.schemas import User

router = APIRouter(prefix="/players", tags=["players"])


@router.get("", response_model=List[User])
def list_players(q: str = None, online: bool = False):
    with DatabaseHandler() as db:
        players = db.get_users(q=q)

    if online:
        players = list(filter(UsersManager.is_online, players))

    return players


@router.get("/{player_id}", response_model=User)
def get_player(player_id: int):
    with DatabaseHandler() as db:
        return db.get_user_by_id(player_id)
