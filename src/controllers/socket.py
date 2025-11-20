import asyncio
import websockets
import json
import time
import random

data = [] #feed a score object

async def collect_data():

    """Simulate data being generated later replace with call to eliminate data"""
    while True:
        new_item = {"value": random.randint(1, 100), "timestamp": time.time()}
        data.append(new_item)
        await asyncio.sleep(1)

async def handler(websocket):
    """Send the array every second to any connected client"""
    while True:
        await websocket.send(json.dumps(data))
        await asyncio.sleep(1)

async def main():
    # Run both collector and websocket server
    collector_task = asyncio.create_task(collect_data())
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await collector_task  # keep running

if __name__ == "__main__":
    asyncio.run(main())
