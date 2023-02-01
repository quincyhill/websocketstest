import asyncio
import websockets

async def hello():
    async with websockets("ws://localhost:8765") as websocket:
        await websocket.send("Hello world!")
        await websocket.recv()

asyncio.run(hello())