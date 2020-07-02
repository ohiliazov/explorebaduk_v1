import asyncio
import datetime

from sgftree import Kifu

from explorebaduk.models.user import User
from explorebaduk.models.timer import TimeControl
from explorebaduk.exceptions import GameStatusError


class GameStatus:
    CREATED = "created"
    PLAYING = "playing"
    PAUSED = "paused"
    SCORING = "scoring"
    FINISHED = "finished"


class GameInfo:
    def __init__(self, black: User, white: User, handicap: int, komi: float):
        self.black = black
        self.white = white
        self.handicap = handicap
        self.komi = komi

    def __str__(self):
        return f"B[{self.black.id}]W[{self.white.id}]HA[{self.handicap}]KM[{self.komi}]"


class GamePlayer:
    def __init__(self, player: User, time_control: TimeControl):
        self.player = player
        self.timer = time_control.timer()

    @property
    def time_left(self):
        return round(self.timer.time_left, 2)

    def start_timer(self):
        return self.timer.start()

    def stop_timer(self):
        return self.timer.stop()


class Game:
    def __init__(self, challenge, game_info):
        self.challenge = challenge
        self.black = GamePlayer(game_info.black, challenge.time_control)
        self.white = GamePlayer(game_info.white, challenge.time_control)
        self.kifu = Kifu.from_game_info(challenge.info, game_info)

        self.status = GameStatus.CREATED

        # will set on game start
        self.started_at = None
        self.game_id = None

        self._timer_task = None

        self.observers = set()

    @property
    def turn(self):
        return self.kifu._turn

    def __str__(self):
        return f"ID[{self.game_id}]B[{self.black.player.id}]W[{self.white.player.id}]{self.challenge.info}"

    @property
    def whose_turn(self) -> GamePlayer:
        return self.black if self.turn == "black" else self.white

    @property
    def opponent(self) -> GamePlayer:
        return self.black if self.turn == "white" else self.white

    async def _out_of_time(self):
        self.status = GameStatus.FINISHED
        await asyncio.gather(
            self.whose_turn.player.send("you lost"),
            self.opponent.player.send("you won"),
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

    async def send(self, message, *, include_observers: bool = False):
        tasks = [self.black.player.send(message), self.white.player.send(message)]

        if include_observers:
            tasks.extend([observer.send(message) for observer in self.observers])

        await asyncio.gather(*tasks)

    async def sync_status(self):
        message = (
            f"game ID[{self.game_id}]ST[{self.status}]PL[{self.turn}]"
            f"BL[{self.black.time_left}]WL[{self.white.time_left}]"
        )
        await self.send(message, include_observers=True)

    async def start_game(self, db_handler):
        if self.status != GameStatus.CREATED:
            raise GameStatusError("The game is already started")

        self.started_at = datetime.datetime.utcnow()
        self.game_id = db_handler.insert_game(
            self.challenge.info.name,
            self.challenge.info.width,
            self.challenge.info.height,
            self.started_at,
            str(self.kifu)
        )

        self.status = GameStatus.PLAYING
        self.start_timer()

        await self.sync_status()

    async def make_move(self, coord):
        if self.status != GameStatus.PLAYING:
            raise GameStatusError("The game is not started")

        try:
            self.kifu.make_move(coord, self.stop_timer())
        except Exception as ex:
            print(ex)
            self.start_timer()

        if self.kifu.board.count_passes > 1:
            self.status = GameStatus.SCORING
        else:
            self.start_timer()

        await self.sync_status()

    async def mark_stone(self, action, coord):
        if self.status != GameStatus.SCORING:
            raise GameStatusError("The game is not finished")

        black_territory, white_territory = self.kifu.mark_stone(action, coord)

        await self.send(f"game ID[{self.game_id}]{black_territory}{white_territory}", include_observers=True)
