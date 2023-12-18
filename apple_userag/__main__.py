from argparse import ArgumentParser
from typing import Literal
import httpx
import asyncio
import json
from tqdm.asyncio import tqdm_asyncio

from . import _data_path

async def get_versions(
    client: httpx.AsyncClient,
    identifier: str,
    semaphore: asyncio.Semaphore,
) -> list:
    async with semaphore:
        response = await client.get( f"https://api.ipsw.me/v4/device/{identifier}",
                                     params={"type": "ipsw"}, )
    return response.json()

async def update() -> None:
    client, semaphore = httpx.AsyncClient(timeout=httpx.Timeout(60)), asyncio.Semaphore(20)
    devices_data = (await client.get("https://api.ipsw.me/v4/devices")).json()
    all_versions = await tqdm_asyncio.gather(*[ get_versions(client, device_data["identifier"], semaphore)
                                                for device_data in devices_data ])
    with open(_data_path, "w") as write:
        json.dump(all_versions, write, indent=4)

def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("action", choices=["update"])
    args = vars(parser.parse_args())

    action: Literal["update"] = args["action"]
    if action == "update":
        asyncio.run(update())
    else:
        parser.error(f'unknown action "{action}"')