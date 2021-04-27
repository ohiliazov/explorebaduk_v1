from typing import List

from fastapi import APIRouter, Depends

from explorebaduk.crud import DatabaseHandler
from explorebaduk.dependencies import get_db_session
from explorebaduk.managers import UsersManager
from explorebaduk.schemas import User

router = APIRouter(prefix="/players", tags=["players"])


@router.get("", response_model=List[User])
def list_players(
    q: str = None,
    online: bool = False,
    db: DatabaseHandler = Depends(get_db_session),
):
    players = db.get_users(q=q)

    if online:
        players = list(filter(UsersManager.is_online, players))

    return players


@router.get("/{player_id}", response_model=User)
def get_player(player_id: int, db: DatabaseHandler = Depends(get_db_session)):
    return db.get_user_by_id(player_id)
