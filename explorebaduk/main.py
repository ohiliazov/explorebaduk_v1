import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from explorebaduk.broadcast import broadcast
from explorebaduk.routers import challenges, players, websocket

app = FastAPI(
    title="ExploreBaduk API",
    on_startup=[broadcast.connect],
    on_shutdown=[broadcast.disconnect],
)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(websocket.router)
app.include_router(players.router)
app.include_router(challenges.router)


if __name__ == "__main__":
    uvicorn.run("explorebaduk.main:app", host="localhost", port=8080, reload=True)
