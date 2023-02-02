import json
import asyncio
import websockets
import itertools
from connect4 import PLAYER1, PLAYER2, Connect4

async def handler(websocket):
    # This implementation is of the websockets documentation with some of my own tweaks.
    # Initialize a Connect Four game.
    game = Connect4()

    # Players take alternate turns, using the same browser.

    # Interesting use of itertools, should read more into the library...
    turns = itertools.cycle([PLAYER1, PLAYER2])
    player = next(turns)

    async for message in websocket:
        # Valid in types
        # {type: 'play', column : INT}

        # Parse a "play" event from the client
        event = json.loads(message)

        # Ensure the input data is valid
        assert event['type'] == 'play'
        assert isinstance(event['column'], int)

        # Now this should also be an int
        column = event['column']

        # Valid out types
        # {type: "play", player: PLAYER, column: INT, row: INT}
        # {type: "win", player: PLAYER}
        # {type: "error", "message": MESSAGE}
        try:
            # Play the move.
            row = game.play(player, column)
        except RuntimeError as e:
            # Send an "error" event if the move was illegal.
            event = {
                "type": "error",
                "message": str(e),
            }
            await websocket.send(json.dumps(event))

            # Skip the rest of the loop. I keep forgetting that continue exists...
            continue

        # Send a "play" event to update client.
        event = {
            "type": "play",
            "player": player,
            "column": column,
            "row": row,
        }

        await websocket.send(json.dumps(event))

        # If move is winning, send a "win" event to update client.
        if game.winner is not None:
            event = {
                "type": "win",
                "player": game.winner,
            }
            await websocket.send(json.dumps(event))
        
        # Alternate turns.
        player = next(turns)



async def main():
    PORT = 8001
    async with websockets.serve(ws_handler=handler, host="", port=PORT):
        print(f"Server started on port {PORT}")
        await asyncio.Future() # Runs forever

if __name__ == "__main__":
    asyncio.run(main())