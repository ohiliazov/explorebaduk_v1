from fastapi.routing import APIRouter

from explorebaduk.crud import get_players_list

router = APIRouter(
    prefix="/api",
)


@router.get("/players")
def get_players(q: str = None):
    return [player.as_dict() for player in get_players_list(q)]
