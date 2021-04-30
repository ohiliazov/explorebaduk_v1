import random

from explorebaduk.models import UserModel
from explorebaduk.schemas import CreatorColor


def resolve_color(creator, opponent: UserModel, creator_color: CreatorColor):
    if creator_color is CreatorColor.BLACK:
        black, white = creator, opponent
    elif creator_color is CreatorColor.WHITE:
        black, white = opponent, creator
    elif creator_color is CreatorColor.NIGIRI:
        black, white = random.sample([creator, opponent], 2)
    else:
        black, white = sorted([creator, opponent], key=lambda user: user.rating)

    return black, white
