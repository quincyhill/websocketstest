import json
import asyncio
# For websockets, just import what I need since it has better intellisense
import websockets
import itertools
import secrets
from connect4 import PLAYER1, PLAYER2, Connect4

# Could define the types but this will still work
JOIN = {}

async def error(websocket, message):
    """Send an error message to a WebSocket connection."""
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))

async def join(websocket, join_key):
    # Find the Connect Four game.
    try:
        game, connected = JOIN[join_key]
    except KeyError:
        await error(websocket, "Invalid join key.")
        return

    # Register to receive moves from this game.
    connected.add(websocket)
    try:
        # Temporary - for testing.
        print("second player joined game", id(game))
        async for message in websocket:
            print("second player sent", message)
    finally:
        # Unregister to stop receiving moves from this game.
        connected.remove(websocket)

async def start(websocket):
    """Start a new game."""
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
    """Handle a WebSocket connection."""
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    if "join" in event:
        # Second player joins an existing game.
        await join(websocket, event["join"])
    else:
        # First player starts a new game.
        await start(websocket)

async def main():
    """Start the server."""
    PORT = 8001
    async with websockets.serve(ws_handler=handler, host="", port=PORT):
        print(f"Server started on port {PORT}")
        await asyncio.Future() # Runs forever

if __name__ == "__main__":
    asyncio.run(main())