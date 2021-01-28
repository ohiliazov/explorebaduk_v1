import asyncio
from typing import Awaitable, Coroutine

from broadcaster import Broadcast

broadcaster = Broadcast("memory://explorebaduk")


async def run_until_first_complete(*coroutines: Awaitable[Coroutine]) -> None:
    tasks = [asyncio.create_task(coroutine) for coroutine in coroutines]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
