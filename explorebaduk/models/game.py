import asyncio
import datetime

from sgftree.sgf import SGF

from explorebaduk.database import DatabaseHandler
from explorebaduk.models.player import Player
from explorebaduk.models.timer import TimeControl


class GameStatus:
    PENDING = "pending"
    PLAYING = "playing"
    SCORING = "scoring"
    FINISHED = "finished"


class GamePlayer:
    def __init__(self, player: Player, time_control: TimeControl):
        self.player = player
        self.timer = time_control.timer()

    @property
    def time_left(self):
        return self.timer.time_left

    def start_timer(self):
        return self.timer.start()

    def stop_timer(self):
        return self.timer.stop()


class Game:
    def __init__(self, data: dict, db_handler: DatabaseHandler):
        self.db_handler = db_handler
        self.name = data["name"]
        self.width = data["width"]
        self.height = data["height"]
        self.time_control = TimeControl(**data)

        self.status = GameStatus.PENDING

        # will set on game start
        self.black = None
        self.white = None
        self.sgf = None
        self.started_at = None
        self.game_id = None

        self._timer_task = None

        self.observers = set()

    @property
    def turn(self):
        return self.sgf.turn

    def __str__(self):
        if self.game_id:
            return (
                f"ID[{self.game_id}]GN[{self.name}]SZ[{self.width}:{self.height}]"
                f"B[{self.black.player.id}]W[{self.white.player.id}]"
            )

        return f"GN[{self.name}]SZ[{self.width}:{self.height}]"

    @property
    def whose_turn(self) -> GamePlayer:
        return self.black if self.turn == "black" else self.white

    @property
    def opponent(self) -> GamePlayer:
        return self.black if self.turn == "white" else self.white

    async def _out_of_time(self):
        self.status = GameStatus.FINISHED
        print(self.whose_turn.time_left)
        print(self.opponent.time_left)
        await asyncio.gather(
            self.whose_turn.player.send("you lost"), self.opponent.player.send("you won"),
        )

    async def _check_timer(self):
        await asyncio.sleep(self.whose_turn.time_left)
        await self._out_of_time()

    def start_timer(self) -> float:
        self._timer_task = asyncio.create_task(self._check_timer())
        return self.whose_turn.timer.start()

    def stop_timer(self) -> float:
        self._timer_task.cancel()
        return self.whose_turn.timer.stop()

    def start_game(self, black: Player, white: Player, handicap, komi):
        self.black = GamePlayer(black, self.time_control)
        self.white = GamePlayer(white, self.time_control)

        self.sgf = SGF(self.width, self.height, handicap, komi)
        self.started_at = datetime.datetime.utcnow()
        self.game_id = self.db_handler.insert_game(self.name, self.width, self.height, self.started_at, str(self.sgf))

        self.status = GameStatus.PLAYING
        self.start_timer()

    async def sync_timers(self):
        message = f"game ID[{self.game_id}]PL[{self.turn}]BL[{self.black.time_left}]WL[{self.white.time_left}]"
        message += "\n" + str(self.sgf.board)
        await asyncio.gather(
            self.black.player.send(message), self.white.player.send(message),
        )

    def make_move(self, coord):
        if self.status == GameStatus.FINISHED:
            raise Exception("Game is finished")

        self.sgf.make_move(coord, self.stop_timer())
        self.start_timer()
