import json
import asyncio
# For websockets, just import what I need since it has better intellisense
import websockets
import secrets
from connect4 import PLAYER1, PLAYER2, Connect4
import logging
logging.basicConfig(format='%(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)

JOIN = {}
WATCH = {}

async def error(websocket, message):
    """Send an outbound error message to a WebSocket connection."""
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))

async def replay(websocket, game):
    """Send previous moves"""
    # Make a copy to avoid an exception if game.loves change while iteration
    # is in progress. If a move is played while replay is running, moves will
    # be sent ouf of order but each move will be sent once and eventually the
    # UI will be consistent.
    for player, column, row in game.moves.copy():
        event = {
            "type": "play",
            "player": player,
            "column": column,
            "row": row,
        }
        await websocket.send(json.dumps(event))

async def watch(websocket, watch_key):
    """Watch a game of Connect Four."""

    # Find the Connect Four game.
    try:
        game, connected = WATCH[watch_key]
    except KeyError:
        await error(websocket, "Invalid watch key.")
        return

    # Register to receive moves from this game.
    connected.add(websocket)
    try:
        # Send previous moves, in case the game already started
        await replay(websocket, game)

        # Keep the connection open, but don't receive any messages.
        await websocket.wait_closed()
    finally:
        # Unregister to stop receiving moves from this game.
        connected.remove(websocket)

async def play(websocket, game: Connect4, player, connected):
    """Recieve and process moves from a player"""

    async for message in websocket:
        # Parse our "play" event from the UI.
        event = json.loads(message)
        assert event["type"] == "play"
        column = event["column"]

        try:
            # Play the move
            row = game.play(player, column)
        except RuntimeError as e:
            # The error should only relay to the websocket that made the move
            await error(websocket, str(e))
            continue

        # Send a "play" event to upgrade all the clients
        event = {
            "type": "play",
            "player": player,
            "column": column,
            "row": row,
        }

        # This is the other way instead of doing the loops
        websockets.broadcast(connected, json.dumps(event))

        # If move is winning, send a "win" event to all clients.
        if game.winner is not None:
            event = {
                "type": "win",
                "player": player,
            }
            # Same change here
            websockets.broadcast(connected, json.dumps(event))
        

async def join(websocket, join_key):
    # Find the Connect Four game.
    # Somewhere in the function the play function is called.
    try:
        game, connected = JOIN[join_key]
    except KeyError:
        await error(websocket, "Invalid join key.")
        return

    # Register to receive moves from this game.
    connected.add(websocket)
    try:
        # Send the frist move, in case the first player already played it
        await replay(websocket, game)

        # Receive and process moves from the second player.
        await play(websocket, game, PLAYER2, connected)
    finally:
        # Unregister to stop receiving moves from this game.
        connected.remove(websocket)

async def start(websocket):
    """Start a new game."""
    # Initialize a Connect Four game, the set of WebSocket connections
    # receiving moves from this game, and secret access token.
    game = Connect4()

    # The connected received the websocket connection of the first player.
    connected = {websocket}

    join_key = secrets.token_urlsafe(12)
    JOIN[join_key] = game, connected

    # Different key from the game
    watch_key = secrets.token_urlsafe(12)
    WATCH[watch_key] = game, connected

    try:
        # Send the secret access token to the browser of the first player,
        # where it'll be used for building a "join" link.
        event = {
            "type": "init",
            "join": join_key,
            "watch": watch_key,
        }
        await websocket.send(json.dumps(event))

        # Here we run the play
        await play(websocket, game, PLAYER1, connected)

    finally:
        del JOIN[join_key]
        # Hm...
        del WATCH[watch_key]


async def handler(websocket):
    """Handle a WebSocket connection."""
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    if "join" in event:
        # Second player joins an existing game.
        await join(websocket, event["join"])
    elif "watch" in event:
        # Watch an existing game.
        await watch(websocket, event["watch"])
    else:
        # First player starts a new game.
        await start(websocket)

async def main():
    """Start the server."""
    PORT = 8001
    async with websockets.serve(ws_handler=handler, host="", port=PORT):
        logger.debug('Server started on port %d', PORT)
        await asyncio.Future() # Runs forever

if __name__ == "__main__":
    asyncio.run(main())