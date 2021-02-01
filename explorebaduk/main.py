from fastapi import FastAPI

from explorebaduk.broadcast import broadcast
from explorebaduk.routers import challenges, players, websocket

app = FastAPI(
    title="ExploreBaduk API",
    on_startup=[broadcast.connect],
    on_shutdown=[broadcast.disconnect],
)
app.include_router(websocket.router)
app.include_router(players.router)
app.include_router(challenges.router)
