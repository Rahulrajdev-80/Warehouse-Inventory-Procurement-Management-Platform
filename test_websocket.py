import asyncio
import websockets


WEBSOCKET_ENDPOINTS = [
    ("inventory", "ws://localhost:8000/ws/inventory"),
    ("alerts", "ws://localhost:8000/ws/alerts"),
    ("transfers", "ws://localhost:8000/ws/transfers"),
]


async def test_websocket(name, uri):
    print("=" * 60)
    print(f"Testing {name}: {uri}")

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected successfully!")

            await websocket.send(f"Hello {name}")

            response = await websocket.recv()

            print("Server response:")
            print(response)

            print(f"{name} WebSocket: SUCCESS")

    except Exception as e:
        print(f"{name} WebSocket: FAILED")
        print(f"Error: {e}")


async def main():
    for name, uri in WEBSOCKET_ENDPOINTS:
        await test_websocket(name, uri)


if __name__ == "__main__":
    asyncio.run(main())