from pathlib import Path
from noneprompt import CheckboxPrompt, Choice
import asyncio

from .model import MetaData
from .download import download

pid_map = {
    "lpack_vckr": "韩文配音",
    "lpack_vcen": "英文配音",
    "lpack_vccsm": "方言配音",
    "lpack_vccn": "中文配音",
    "lpack_vcjp": "日文配音",
    "lpack_music": "音乐",
}


async def main(all: bool = True, only_download: bool = False, output: Path = Path("download")):
    metadata = await MetaData.get()
    if not all:
        download_types = CheckboxPrompt(
            "请选择你需要的类型",
            [
                Choice(
                    f"{i.name}{f' ---> {pid_map.get(i.name)}' if pid_map.get(i.name) else ''}",
                    i.name,
                )
                for i in metadata.update_list.packInfos
            ],
            annotation="使用键盘的 ↑ 和 ↓ 来选择, 按空格开关, 按回车确认",
        ).prompt()
        download_types = [i.data for i in download_types]
    else:
        download_types = [i.name for i in metadata.update_list.packInfos]
    

    await download(download_types, metadata, output)

def run(all: bool = True, only_download: bool = False, output: Path = Path("download")):
    asyncio.run(main(all, only_download, output))