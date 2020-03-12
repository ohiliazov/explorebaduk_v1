async def handle_game_move(ws, data: dict):
    pos = data["pos"]
    return await ws.send(f"You played {pos}")
