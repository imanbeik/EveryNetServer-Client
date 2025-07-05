import websockets
import asyncio
import requests
import json
import base64
import config


ACCESS_TOKEN = None
PORT = 80
URI = f'ws://{config.SERVER_DOMAIN}:8080'

async def forwarder():
    global PORT, URI
    async with websockets.connect(URI, extra_headers=[('access_token', ACCESS_TOKEN)]) as websocket:
        print("Connected to WebSocket. Type 'exit' to quit.")
        await receive_and_respond(websocket)

async def receive_and_respond(websocket):
    try:
        async for message in websocket:
            print(f"\nReceived: {message}")
            message = json.loads(message)

            if message["type"] == "request":
                full_request = message["data"]
                
                print(f"http://localhost:{PORT}{full_request['path']}")
                
                # full_request['headers'].pop('Connection')
                full_request['headers']["Host"] = "localhost"

                print(full_request['headers'])

                if full_request["method"] == "GET":
                    ans = requests.get(
                        f"http://localhost:{PORT}{full_request['path']}",
                        headers=full_request['headers'],
                        timeout=5
                    )
                else:
                    ans = requests.post(
                        f"http://localhost:{PORT}{full_request['path']}",
                        headers=full_request['headers'],
                        data=full_request['params'], timeout=5
                    )
                
                print("Request done")
                headers = {}
                for k, v in ans.headers.items():
                    headers[k] = v
                
                response = {'content': base64.b64encode(ans.content).decode('ascii'), 'headers': headers, 'code': ans.status_code, 'id': full_request['id']}
                response_json = json.dumps(response)
                
                await websocket.send(response_json)

            elif message["type"] == "alert":
                print(message["data"])
    except websockets.ConnectionClosed:
        print("Receiver stopped: Connection closed.")

if __name__ == "__main__":

    if not config.AUTH_SAVED:
        PORT = input("Enter port you wanna requests forward to it: ")
        ACCESS_TOKEN = input("Enter your access token: ")
    else:
        PORT = config.PORT
        ACCESS_TOKEN = config.ACCESS_TOKEN

    try:
        asyncio.run(forwarder())
    except KeyboardInterrupt:
        pass

    print("Server stopped")
