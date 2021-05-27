import websockets
import asyncio
import requests
import json

ACCESS_TOKEN = None
PORT = None
URI = 'ws://everynetserver.ga:8924'

async def forwarder():
    global PORT, URI
    async with websockets.connect(URI, extra_headers=[('access_token', ACCESS_TOKEN)]) as websocket:
        while True:
            full_request_json = await websocket.recv()
            full_request = json.loads(full_request_json)
            
            if full_request["method"] == "GET":
                ans = requests.get(f"http://localhost{full_request['path']}:{PORT}", headers=full_request['headers'])
            else:
                ans = requests.post(f"http://localhost{full_request['path']}:{PORT}", headers=full_request['headers'])
            
            response = {}
            response['text'] = ans.text
            response['headers'] = ans.headers
            response_json = json.dumps(response)
            
            await websocket.send(response_json)

if __name__ == "__main__":
    PORT = input("Enter port you wanna requests forward to it: ")
    ACCESS_TOKEN = input("Enter your access token: ")
    
    try:
        asyncio.get_event_loop().run_until_complete(forwarder())
    except KeyboardInterrupt:
        pass
    
    print("Server stopped")