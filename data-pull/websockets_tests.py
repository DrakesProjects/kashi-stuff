import os
import sys
import argparse
import asyncio
import json
from typing import Tuple
from websockets.asyncio.client import connect
from keyloader import make_headers

API_PATH = "/trade-api/ws/v2"

# URL IS WHERE WE SPECIFY DEMO OR PROD MODE with 'demo-api' or just 'api'
API_URL = "wss://api.elections.kalshi.com" + API_PATH


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


async def run_ws(headers: Tuple[str, str, str]):
    """Connect to the kalshi PROD WebSocket endpoint using api_key"""
    try:
        async with connect(API_URL, additional_headers=headers) as ws:
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

    except Exception as e:
        print("WebSocket connection error:", e)


async def main():
    # Parse file location of private key and file location of access key from environment variables
    private_key_path = os.environ["PRIVATE_KEY_PATH"]
    access_key_path = os.environ["ACCESS_KEY_PATH"]
    headers = make_headers(access_key_path,
                           private_key_path,
                           'GET',
                           API_PATH)
    await run_ws(headers)
    

if __name__ == "__main__":
    asyncio.run(main())
