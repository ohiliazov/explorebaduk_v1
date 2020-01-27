import asyncio
import logging
from typing import List, Tuple

from explorebaduk.constants import AUTO_MATCH_DELAY
from explorebaduk.server import LOBBY

logger = logging.getLogger('matchmaker')


# TODO: implement
async def matchmaker() -> List[Tuple]:
    """
    Return data in format <player1> <player2> <time_settings>
    :return:
    """
    logger.info(f'current lobby: {LOBBY}')
    return []


# TODO: implement
async def start_game(data):
    logger.info(f'Starting game: {data}')


async def auto_match_manager():
    """
    Coroutine that monitors lobby for match
    :return:
    """
    logger.info('Starting auto-match system')
    while True:
        matches = await matchmaker()

        for match in matches:
            await start_game(match)
        else:
            logger.info(f'Matches found: {len(matches)}')
        await asyncio.sleep(AUTO_MATCH_DELAY)


# TODO: implement
async def handle_auto_match(ws, data: dict):
    """
    Handles auto-match message
    :param ws:
    :param data: contains time settings, lower and upper rating bounds
    :return:
    """
    logger.info(f'Incoming data: {data}')
