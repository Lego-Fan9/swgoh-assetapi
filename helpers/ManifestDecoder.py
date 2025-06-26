from helpers import ManifestDecoderHelper, Logger
from helpers.RequestManager import RequestManager
from helpers.FileLock import GlobalFileLock as FileLock
from helpers.TypeHelpers import AssetOS
from typing import Dict, List, Any
import aiofiles
import asyncio
import json
import os

logger = Logger.getLogger("getManifest")

def decodeManifest(manifest: bytes) -> List[Dict[str, Any]]:
    manifestWorker = ManifestDecoderHelper.RawAssetManifest() # type: ignore
    manifestWorker.ParseFromString(manifest)

    response: List[Dict[str, Any]] = []
    for record in manifestWorker.records:
        recordName = [entry.asset_name for entry in record.entries][0]
        prefix = record.name.split('_')[0]
        response.append({"name": record.name, "fullname": recordName, "version": record.version, "prefix": prefix})
        
    return response

async def saveManifest(version: int, assetOS: AssetOS, decoded_manifest: List[Dict[str, Any]]):
    try:
        os.makedirs('tmp/manifest', exist_ok=True)
        async with FileLock.claimFile(os.path.abspath(f'tmp/manifest/manifest_{assetOS}_{version}.json')):
            async with aiofiles.open(f'tmp/manifest/manifest_{assetOS}_{version}.json', 'w') as file:
                json_str = json.dumps(decoded_manifest, indent=4)
                await file.write(json_str)
    except Exception as e:
        logger.error(f'Error in saveManifest: {e}')
        raise e

async def getAssetManifest(version: int, assetOS: AssetOS=AssetOS.WINDOWS) -> List[str]:
    decoded_manifest = decodeManifest(await RequestManager.getAsset("manifest.data", version, assetOS, "content")) # type: ignore
    asyncio.create_task(saveManifest(version, assetOS, decoded_manifest))

    response = []
    for object in decoded_manifest:
        response.append(object["name"])

    return response

async def getAssetManifestBlocking(version: int, assetOS: AssetOS=AssetOS.WINDOWS) -> List[str]:
    decoded_manifest = decodeManifest(await RequestManager.getAsset("manifest.data", version, assetOS, "content")) # type: ignore
    await saveManifest(version, assetOS, decoded_manifest)

    response = []
    for object in decoded_manifest:
        response.append(object["name"])

    return response