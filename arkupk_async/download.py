import asyncio
import hashlib
import zipfile
import time
from pathlib import Path
from io import BytesIO

import click
import httpx
from httpx import AsyncClient

from .model import MetaData, abInfo


class ToolBox:

    # counter
    start_time: float
    complete = 0
    total = 0

    # async downloader
    client: AsyncClient
    sem: asyncio.Semaphore

    def __init__(self, client: AsyncClient, sem: asyncio.Semaphore = asyncio.Semaphore(100)):
        self.start_time = time.time()
        self.client = client
        self.sem = sem

    def complete_download(self, filename):
        self.complete += 1
        self.logger(filename, "bright_green")

    def expect_download(self, filename):
        self.complete += 1
        self.logger(filename, "bright_red")

    def logger(self, log: str, fg: str):
        click.secho(
            f"[{self.complete:4}/{self.total:4}]{int(time.time()-self.start_time):5}s: {log}",
            fg=fg,
        )


async def _download(url: str, ab: abInfo, download_path: Path, tool: ToolBox):
    async with tool.sem:
        resp = await tool.client.get(url)
        if resp.status_code != 200:
            tool.expect_download(ab.name)
            return
        data = resp.content
        if len(data) == ab.totalSize:
            with zipfile.ZipFile(BytesIO(data)) as zipf:
                zipf.extractall(download_path)
            tool.complete_download(ab.name)
        else:
            tool.expect_download(ab.name)


async def download(download_types: list[str], metadata: MetaData, base_path: Path):
    tool = ToolBox(client=httpx.AsyncClient())

    ab_infos = metadata.update_list.abInfos
    ab_infos = [i for i in ab_infos if i.pid in download_types]
    download_path = base_path.joinpath("download")
    tool.total = len(ab_infos)

    tasks = []
    for ab in ab_infos:
        path = download_path.joinpath(ab.name)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            file_md5 = hashlib.md5(path.read_bytes()).hexdigest()
            if file_md5 == ab.md5:
                tool.total -= 1
                tool.logger(ab.name, fg="bright_green")
                continue
            else:
                tool.logger(f"{ab.name} exists but md5 is not correct", fg="bright_yellow")

        download_name: str = ab.name.replace("/", "_").replace("#", "__")
        download_name = download_name.split(".")[0] + ".dat"

        tasks.append(
            await asyncio.create_task(
                _download(
                    f"https://ak.hycdn.cn/assetbundle/official/Android/assets/{metadata.version.resVersion}/{download_name}",
                    ab,
                    download_path,
                    tool,
                )
            )
        )

    await asyncio.gather(*tasks)
