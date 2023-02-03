import asyncio
import pathlib
import ssl
from websockets import server
import logging

async def hello(websocket: server.WebSocketServerProtocol):
    """Simple server that responds with hello prepended to the input"""
    name = await websocket.recv()
    greeting = f"Hello {name}"
    await websocket.send(greeting)

# Check up on some docs here
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

# Hm.... gotta see what this pem file is...
localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")

ssl_context.load_cert_chain(localhost_pem)

async def main():
    """Main function"""
    async with server.serve(hello, "localhost", 8765, ssl=ssl_context):
        await asyncio.Future() # run forever