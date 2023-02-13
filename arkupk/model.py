from typing import Optional
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
