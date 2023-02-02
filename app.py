import json
import asyncio
import websockets
from connect4 import PLAYER1, PLAYER2, Connect4

async def handler(websocket):
    # Game is master state
    game = Connect4()

    async for message in websocket:
        # Valid in types
        # {type: 'play', column : INT}

        data = json.loads(message)

        # Ensure the input data is valid
        assert data['type'] == 'play'
        assert type(data['column']) == int

        # Valid out types
        # {type: "play", player: PLAYER, column: INT, row: INT}
        # {type: "win", player: PLAYER}
        # {type: "error", "message": MESSAGE}

        current_player = PLAYER2 if len(game.moves) % 2 else PLAYER1

        try:
            row = game.play(current_player, data['column'])
            res = {'type': 'play', 'player': current_player, 'column': data['column'], 'row': row}

            await websocket.send(json.dumps(res))

            if game.last_player_won:
                res = {'type': 'win', 'player': game.last_player}
                await websocket.send(json.dumps(res))

        except Exception as e:
            res = {'type': 'error', 'message': str(e)}
            await websocket.send(json.dumps(res))

async def main():
    PORT = 8001
    async with websockets.serve(ws_handler=handler, host="", port=PORT):
        print(f"Server started on port {PORT}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())