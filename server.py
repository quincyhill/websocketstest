import asyncio

from websockets import server
import logging

logging.basicConfig(format='%(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)

async def hello(websocket: server.WebSocketServerProtocol):
    """Just opens a connection receives name sends a greeting then closes the connection"""
    name = await websocket.recv()
    greeting = f"Hello {name}"
    await websocket.send(greeting)

async def main():
    logger.debug("Server started")
    async with server.serve(hello, "localhost", 8765):
        await asyncio.Future() #run forever

if __name__ == "__main__":
    asyncio.run(main())