from typing import Optional

import httpx
from pydantic import BaseModel


class abInfo(BaseModel):
    name: str
    hash: str
    md5: str
    totalSize: int
    abSize: int
    thash: Optional[str]
    pid: Optional[str]
    cid: int


class packInfo(BaseModel):
    name: str
    hash: str
    md5: str
    totalSize: int
    abSize: int
    cid: int


class UpdateList(BaseModel):
    versionId: str
    abInfos: list[abInfo]
    countOfTypedRes: int
    packInfos: list[packInfo]


class Version(BaseModel):
    resVersion: str
    clientVersion: str


class MetaData(BaseModel):
    update_list: UpdateList
    version: Version

    @classmethod
    async def get(cls):
        async with httpx.AsyncClient() as client:
            v = await client.get(
                "https://ak-conf.hypergryph.com/config/prod/official/Android/version"
            )
            version = Version(**v.json())
            u = await client.get(
                f"https://ak.hycdn.cn/assetbundle/official/Android/assets/{version.resVersion}/hot_update_list.json"
            )
            update_list = UpdateList(**u.json())
        return cls(update_list=update_list, version=version)
