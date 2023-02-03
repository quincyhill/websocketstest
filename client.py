import asyncio
from websockets import client


async def hello():
    uri = "ws://localhost:8765"
    async with client.connect(uri) as websocket:
        name = input("What's your name? ")
        await websocket.send(name)
        greeting = await websocket.recv()

if __name__ == "__main__":
    asyncio.run(hello())