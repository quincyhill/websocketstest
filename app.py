import json
import asyncio
import websockets
from connect4 import PLAYER1, PLAYER2, Connect4

async def handler(websocket):
    game = Connect4()
    row_count = 0
    async for message in websocket:
        # The only data coming from the client is {'type': 'play', column : int}
        data = json.loads(message)

        # Each click will just add to the first column for the red player, just for now
        res =  {'type': 'play', 'player': PLAYER1, 'column': 0, 'row': row_count}
        
        await websocket.send(json.dumps(res))

        row_count += 1

async def main():
    async with websockets.serve(ws_handler=handler, host="", port=8001):
        print("Server started")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())