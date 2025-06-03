import argparse
import asyncio
import json
import websockets
import sys

API_URL = "wss://api.elections.kalshi.com/trade-api/ws/v2"

def get_api_key(key_loc: str) -> str:
    """Read the api key file location, find the api key, and return it"""
    try:
        with open(key_loc, "r", encoding="utf-8") as f:
            key = f.read().strip()
            if not key:
                raise ValueError("API key file is empty")
            return key
    except FileNotFoundError:
        print(f"Error: cannot find file \'{key_loc}\'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading API key from \'{key_loc}\'", file=sys.stderr)
        sys.exit(1)

async def run_ws(api_key: str):
    """Connect to the kalshi PROD WebSocket endpoint using api_key"""
    headers = [("Authorization", f"Bearer {api_key}")]
    try:
        async with websockets.connect(API_URL, extra_headers=headers) as ws:
            print("Connected to Kalshi PROD WebSocket")
            # Subscribe to channels here: #######################

            #####################################################
            async for raw_msg in ws:
                if isinstance(raw_msg, bytes):
                    # Handle Binary Data input
                    print("Received binary frame ({} bytes)".format(len(raw_msg)))
                else:
                    # Handle non-binary input
                    try: # JSON
                        payload = json.loads(raw_msg)
                        print("Recieved JSON:", payload)
                    except: # Other
                        print("Received non-JSON payload:", raw_msg)

    except websockets.InvalidStatusCode as e:
        print(f"Failed to connect: HTTP status {e.status_code}")
    except Exception as e:
        print("WebSocket connection error:", e)

async def main():
    # Parse file location of API key
    parser = argparse.ArgumentParser()
    parser.add_argument("key_loc", required=True, help="Path to a file containing your API key")
    args = parser.parse_args()
    api_key = get_api_key(args.key_loc)
    await run_ws(api_key)

if __name__ == "__main__":
    asyncio.run(main())
