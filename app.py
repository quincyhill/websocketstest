import json
import asyncio
import websockets
from connect4 import PLAYER1, PLAYER2

async def handler(websocket):
    for player, column, row in [
        (PLAYER1, 3, 0),
        (PLAYER2, 3, 1),
        (PLAYER1, 4, 0),
        (PLAYER2, 4, 1),
        (PLAYER1, 2, 0),
        (PLAYER2, 1, 0),
        (PLAYER1, 5, 0),
    ]:
        event = {
            "type": "play",
            "player": player,
            "column": column,
            "row": row
        }

        await websocket.send(json.dumps(event))
        # Sleep for 0.5 seconds to simulate a human player
        await asyncio.sleep(0.5)
    event = {
        "type": "win",
        "player": PLAYER1
    }

    # Send the win event
    await websocket.send(json.dumps(event))

async def main():
    async with websockets.serve(ws_handler=handler, host="", port=8001):
        print("Server started")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())