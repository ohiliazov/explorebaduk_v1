from typing import List

from fastapi import APIRouter

from ..crud import get_players_list
from ..schemas import PlayerOut

router = APIRouter(prefix="/players")


@router.get("", response_model=List[PlayerOut])
def get_players(q: str = None):
    return [player.asdict() for player in get_players_list(search_string=q)]
