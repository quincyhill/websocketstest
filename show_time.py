import asyncio
from datetime import datetime
import random
import time
from websockets.server import serve, WebSocketServerProtocol

async def show_time(websocket: WebSocketServerProtocol):
    """Shows the current time at random intervals"""
    while True:
        message = datetime.utcnow().isoformat() + "Z"
        await websocket.send(message=message)
        await asyncio.sleep(random.random() * 2 + 1)

async def main():
    PORT = 8765
    async with serve(ws_handler=show_time, host="localhost", port=PORT):
        print(f"server started on port {PORT}")
        await asyncio.Future() # run forever

if __name__ == "__main__":
    asyncio.run(main())