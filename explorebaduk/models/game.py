from explorebaduk.gameplay.kifu import Kifu


class Game:
    def __init__(self, width: int, height: int, turn: str, handicap: int, komi: float):
        self.kifu = Kifu(width, height, turn)
        self.handicap = handicap
        self.komi = komi
