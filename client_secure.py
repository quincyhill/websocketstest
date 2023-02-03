import asyncio
import pathlib
import ssl
from websockets import client

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
ssl_context.load_verify_locations(localhost_pem)

async def hello():
    """Secure client"""
    uri = "wss://localhost:8765"
    async with client.connect(uri=uri, ssl=ssl_context) as websocket:
        name = input("What's your name? ")

        await websocket.send(name)
        await websocket.recv()

if __name__ == "__main__":
    asyncio.run(hello())