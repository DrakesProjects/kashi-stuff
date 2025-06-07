# 2025-06-05
# The program is going to be for continuously storing data
# periodically resetting markets, such as the bitcoin pricing
# or weather markets.
from os import environ
import argparse
import asyncio
import json
from typing import Tuple
from websockets.asyncio.client import connect
from keyloader import make_headers

API_PATH = "/trade-api/ws/v2"

# URL IS WHERE WE SPECIFY DEMO OR PROD MODE with 'demo-api' or just 'api'
API_URL = "wss://api.elections.kalshi.com" + API_PATH

async def run_ws(headers: Tuple[str, str, str]):
    """Connect to the kalshi PROD WebSocket endpoint using api_key"""
    try:
        async with connect(API_URL, additional_headers=headers) as ws:
            print("Connected to Kalshi WebSocket")
            # Subscribe to channels here: #######################
            await ws.send(json.dumps({"id": 1,
                                      "cmd": "subscribe",
                                      "params": {
                                          "channels": ["orderbook_delta"],
                                          "market_tickers": ["KXBTCD-25JUN0500-T104999.99"]}
                                      }))
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
    private_key_path = environ["PRIVATE_KEY_PATH"]
    access_key_path = environ["ACCESS_KEY_PATH"]
    headers = make_headers(access_key_path,
                           private_key_path,
                           'GET',
                           API_PATH)
    await run_ws(headers)


if __name__ == "__main__":
    asyncio.run(main())


