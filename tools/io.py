import json

import aiofiles


async def download_file(filename: str, url: str):
    import aiohttp

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"failed to download {url}")
            async with aiofiles.open(filename, mode="wb") as f:
                await f.write(await resp.read())
                await f.close()


def read_json(filename: str) -> dict:
    with open(filename, mode="r") as f:
        return json.load(f)


def write_log(filename: str, data: str, append: bool = True):
    m = "a" if append else "w"
    with open(filename, mode=m) as f:
        f.write(data)
