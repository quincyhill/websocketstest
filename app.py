import json
import asyncio
# For websockets, just import what I need since it has better intellisense
import websockets
import itertools
import secrets
from connect4 import PLAYER1, PLAYER2, Connect4

JOIN = {}


async def start(websocket):
    # Initialize a Connect Four game, the set of WebSocket connections
    # receiving moves from this game, and secret access token.
    game = Connect4()
    connected = {websocket}

    join_key = secrets.token_urlsafe(12)
    JOIN[join_key] = game, connected

    try:
        # Send the secret access token to the browser of the first player,
        # where it'll be used for building a "join" link.
        event = {
            "type": "init",
            "join": join_key,
        }
        await websocket.send(json.dumps(event))

        # Temporary - for testing.
        print("first player started game", id(game))
        async for message in websocket:
            print("first player sent", message)

    finally:
        del JOIN[join_key]


async def handler(websocket):
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    # First player starts a new game.
    await start(websocket)

async def main():
    PORT = 8001
    async with websockets.serve(ws_handler=handler, host="", port=PORT):
        print(f"Server started on port {PORT}")
        await asyncio.Future() # Runs forever

if __name__ == "__main__":
    asyncio.run(main())