from typing import List

from fastapi import APIRouter

from ..crud import get_player_by_id, get_players_list
from ..schemas import PlayerOut

router = APIRouter(prefix="/players", tags=["players"])


@router.get("", response_model=List[PlayerOut])
def get_players(q: str = None):
    return [player.asdict() for player in get_players_list(search_string=q)]


@router.get("/{player_id}", response_model=PlayerOut)
def get_player(player_id: int):
    return get_player_by_id(player_id).asdict()
