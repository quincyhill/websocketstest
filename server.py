import asyncio
import websockets

async def echo(websocket):
    async for message in websocket:
        await websocket.send(message + " [echoed]")

async def main():
    async with websockets.serve(echo, "localhost", 8765):
        print("Server started")
        await asyncio.Future()  # run forever

asyncio.run(main())