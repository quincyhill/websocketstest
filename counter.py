import asyncio
import json
import logging
from websockets.server import serve, WebSocketServerProtocol
from websockets.legacy.protocol import broadcast

logging.basicConfig()

# These varaibles are shared
USERS = set()
VALUE = 0

def users_event() -> str:
    return json.dumps({"type": "users", "count": len(USERS)})

def value_event() -> str:
    return json.dumps({"type": "value", "value": VALUE})

async def counter(websocket: WebSocketServerProtocol) -> None:
    global USERS, VALUE
    try:
        # Register user
        USERS.add(websocket)
        broadcast(USERS, users_event())

        # Send current state to user
        await websocket.send(value_event())
        
        # Manage state changes
        async for message in websocket:
            event = json.loads(message)
            if event["action"] == "minus":
                VALUE -= 1
                broadcast(USERS, value_event())
            elif event["action"] == "plus":
                VALUE += 1
                broadcast(USERS, value_event())
            else:
                logging.error("unsupported event: %s", event)
    finally:
        # Unregister user
        USERS.remove(websocket)
        broadcast(USERS, users_event())

async def main():
    PORT = 6789
    async with serve(ws_handler=counter, host="localhost", port=PORT):
        print(f"server started on port {PORT}")
        await asyncio.Future() # run forever

if __name__ == "__main__":
    asyncio.run(main())