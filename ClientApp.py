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
        while True:
            message = json.loads(await websocket.recv())
            if message["type"] == "request":
                full_request = message["data"]

                if full_request["method"] == "GET":
                    ans = requests.get(f"http://localhost:{PORT}{full_request['path']}",
                                       headers=full_request['headers'])
                else:
                    ans = requests.post(f"http://localhost:{PORT}{full_request['path']}",
                                        headers=full_request['headers'],
                                        data=full_request['params'])

                headers = {}
                for k, v in ans.headers.items():
                    headers[k] = v
                
                response = {'content': base64.b64encode(ans.content).decode('ascii'), 'headers': headers, 'code': ans.status_code, 'id': full_request['id']}
                response_json = json.dumps(response)
                
                await websocket.send(response_json)

            elif message["type"] == "alert":
                print(message["data"])


if __name__ == "__main__":
    PORT = input("Enter port you wanna requests forward to it: ")
    ACCESS_TOKEN = input("Enter your access token: ")


    try:
        asyncio.run(forwarder())
    except KeyboardInterrupt:
        pass

    print("Server stopped")
