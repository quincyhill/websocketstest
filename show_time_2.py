import asyncio
from datetime import datetime
import random
from websockets.server import serve, WebSocketServerProtocol
from websockets.legacy.protocol import broadcast
from typing import Set

CONNECTIONS: Set[WebSocketServerProtocol] = set()

async def register(websocket: WebSocketServerProtocol) -> None:
    CONNECTIONS.add(websocket)
    try:
        await websocket.wait_closed() # This keeps it open
    finally:
        CONNECTIONS.remove(websocket)

async def show_time() -> None:
    while True:
        message = datetime.utcnow().isoformat() + "Z"
        broadcast(websockets=CONNECTIONS, message=message)
        await asyncio.sleep(random.random() * 2 + 1)

async def main():
    PORT = 5678
    async with serve(ws_handler=register, host="localhost", port=PORT):
        print(f"server started on port {PORT}")
        await show_time()

if __name__ == "__main__":
    asyncio.run(main())