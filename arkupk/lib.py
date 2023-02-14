import httpx
import zipfile
import hashlib
#import unitypack


from io import BytesIO
from tqdm import tqdm
from pathlib import Path
#from unitypack.utils import extract_audioclip_samples

from .model import Version, MetaData, UpdateList


def get_metadata():
    version = Version(
        **httpx.get(
            "https://ak-conf.hypergryph.com/config/prod/official/Android/version"
        ).json()
    )
    update_list = UpdateList(
        **httpx.get(
            f"https://ak.hycdn.cn/assetbundle/official/Android/assets/{version.resVersion}/hot_update_list.json"
        ).json()
    )

    return MetaData(version=version, update_list=update_list)


def download(
    download_types: list[str], metadata: MetaData, base_path: Path, unpuck: bool = True
):
    ab_infos = metadata.update_list.abInfos
    ab_infos = [i for i in ab_infos if i.pid in download_types]
    download_path = base_path.joinpath("download")
    for ab in tqdm(ab_infos, desc="Downloading"):
        path = download_path.joinpath(ab.name)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            file_md5 = hashlib.md5(path.read_bytes()).hexdigest()
            if file_md5 == ab.md5:
                tqdm.write(f"{ab.name} already exists")
                continue
            else:
                tqdm.write(f"{ab.name} exists but md5 is not correct")

        download_name: str = ab.name.replace("/", "_").replace("#", "__")
        download_name = download_name.split(".")[0] + ".dat"

        resp = httpx.get(
            f"https://ak.hycdn.cn/assetbundle/official/Android/assets/{metadata.version.resVersion}/{download_name}"
        )
        if resp.status_code == 200:
            data = resp.content
            if len(data) == ab.totalSize:
                tqdm.write(f"{ab.name}")
                with zipfile.ZipFile(BytesIO(data)) as zipf:
                    zipf.extractall(download_path)
            else:
                tqdm.write(f"{ab.name} size error")
        else:
            tqdm.write(str(resp.status_code))
            tqdm.write(f"{ab}")
            break

    #if unpuck:
    #    for ab in tqdm(list(download_path.glob("**/*.ab")), desc="Unpacking"):
    #        if ab.is_file():
    #            unpuck_file(ab, base_path.joinpath("unpacked"))


#def unpuck_file(file: Path, destination_folder: Path):
#    destination_folder = destination_folder.joinpath(*file.parts[2:-1], file.stem)
#    with file.open("rb") as f:
#        bundle = unitypack.load(f)
#        for asset in bundle.assets:
#            for id, object in asset.objects.items():
#                if object.type == "AudioClip":
#                    destination_folder.mkdir(parents=True, exist_ok=True)
#                    for filename, sample in extract_audioclip_samples(object.read()).items():
#                        output_path = destination_folder.joinpath(filename)
#                        output_path.write_bytes(sample)
