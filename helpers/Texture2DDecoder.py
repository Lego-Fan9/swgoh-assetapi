from helpers.Logger import getLogger
from helpers.FileLock import GlobalFileLock as FileLock
from PIL import Image
from typing import Tuple, Dict, List, Union
from io import BytesIO
import UnityPy
import base64
import os

logger = getLogger('texture2DDecoder')

class NoAssetFoundError(Exception):
    pass

async def decodeAsset(filepath: str) -> Tuple[Image.Image, str]:
    async with FileLock.claimFile(os.path.abspath(filepath)):
        env = UnityPy.load(filepath)

    for obj in env.objects:
        if obj.type.name in ["Texture2D", "Sprite"]:
                data = obj.read()
                img_name = data.m_Name
                img = data.image

                return img, img_name
        
    raise NoAssetFoundError(f'No supported assets found in {filepath}')

def imgToB64(image: Image.Image, format: str='PNG') -> str:
    buffered = BytesIO()
    image.save(buffered, format=format)
    img_bytes = buffered.getvalue()
    base64_img = base64.b64encode(img_bytes).decode('utf-8')

    return f"data:image/png;base64,{base64_img}"

async def decodeManyAssets(filepath: str) -> List[Dict[str, Union[str, bool]]]:
    async with FileLock.claimFile(os.path.abspath(filepath)):
        env = UnityPy.load(filepath)

    response: List[Dict[str, Union[str, bool]]] = []
    for obj in env.objects:
        if obj.type.name in ["Texture2D", "Sprite"]:
                data = obj.read()
                img_name = data.m_Name
                # This if statment is to catch empty images such as in shared_resourcecontainer.bundle "Font Texture"
                # Not catching these causes a PermissionError when running data.image
                # The error stems from not having m_StreamData.path or another format that may be used
                # To ensure that an asset exists please check "pass"
                if obj.type.name == "Texture2D":
                     if data.m_StreamData.path == "" and data.m_ImageCount == 0 and data.m_Width == 0:
                          response.append({
                                "name": img_name,
                                "img": "",
                                "valid": False
                            })
                          continue
                     
                img = data.image

                response.append({
                     "name": img_name,
                     "img": imgToB64(img),
                     "valid": True
                })

    return response