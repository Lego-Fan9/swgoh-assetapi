from fastapi import Response
from fastapi.responses import FileResponse
from helpers import Texture2DDecoder, ManifestDecoder, ManifestDiff, Logger
from helpers.RequestManager import RequestManager
from helpers.FileLock import GlobalFileLock as FileLock
from helpers.TypeHelpers import AssetOS, DiffVersion
from typing import Dict, Union, List, Any
import aiofiles
import json
import os
import io

logger = Logger.getLogger('Endpoints')

async def assetSingle(version: int, 
                      assetName: str, 
                      forceReDownload: bool=False, 
                      assetOS: AssetOS=AssetOS.WINDOWS
                      ) -> Response:
    match assetOS:
        case 1:
            bundlePathFormat = 'tmp/bundles/android/{}{}'
        case 2:
            bundlePathFormat = 'tmp/bundles/ios/{}{}'
        case _:
            bundlePathFormat = 'tmp/bundles/windows/{}{}'

    match assetName.split('_')[0]:
            case 'audio':
                assetExtension = '.wwpkg'
            case _:
                assetExtension = '.bundle'

    bundlePath = bundlePathFormat.format(assetName, assetExtension)

    if not os.path.isfile(bundlePath) or forceReDownload:
        logger.debug(f'Downloading {assetName}{assetExtension}')
        await RequestManager.getSaveAsset(assetName + assetExtension, version, bundlePath)

    image, returnName = await Texture2DDecoder.decodeAsset(bundlePath)
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return Response(
        content=img_bytes.getvalue(),
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="{returnName + '.png'}"'}
    )

async def assetMany(version: int, 
                    assetNames: str, 
                    forceReDownload: bool=False, 
                    assetOS: AssetOS=AssetOS.WINDOWS
                    ) -> List[Dict[str, Union[str, List[Dict[str, Union[str, bool]]]]]]:
    match assetOS:
        case 1:
            assetPath = 'tmp/bundles/android/{}{}'
        case 2:
            assetPath = 'tmp/bundles/ios/{}{}'
        case _:
            assetPath = 'tmp/bundles/windows/{}{}'
            
    response = []
    assetNamesList = [name.strip() for name in assetNames.split(',') if name.strip()]

    for assetName in assetNamesList:
        match assetName.split('_')[0]:
            case 'audio':
                assetExtension = '.wwpkg'
            case _:
                assetExtension = '.bundle'
        asset_path = assetPath.format(assetName, assetExtension)
        if not os.path.isfile(asset_path) or forceReDownload:
            logger.debug(f'Downloading {assetName}{assetExtension}')
            await RequestManager.getSaveAsset(assetName+assetExtension, version, asset_path)

        try:
            response.append({"assetName": assetName, "assetData": await Texture2DDecoder.decodeManyAssets(asset_path)})
        except Exception as e:
            logger.exception(f"Failed to decode asset {assetName}: {e}")
            response.append({"error": str(e)})

    return response

async def assetList(version: int, 
                    forceReDownload: bool=False, 
                    assetOS: AssetOS=AssetOS.WINDOWS
                    ) -> List[str]:
    if os.path.isfile(f'tmp/manifest/manifest_{assetOS}_{version}.json') and not forceReDownload:
        async with FileLock.claimFile(os.path.abspath(f'tmp/manifest/manifest_{assetOS}_{version}.json')):
            async with aiofiles.open(f'tmp/manifest/manifest_{assetOS}_{version}.json', 'r') as file:
                content = await file.read()
                
                entries = json.loads(content)
                response = []
                for entry in entries:
                    response.append(entry['name'])
                    
                return response
    else:
        logger.debug("Couldn't find manifest or user requested a new one")

        return await ManifestDecoder.getAssetManifest(version, assetOS)
    
async def assetListDiff(version: int, 
                        diffVersion: int, 
                        forceReDownload: bool=False, 
                        diffType: DiffVersion=DiffVersion.ALL, 
                        prefix: str='None', 
                        assetOS: AssetOS=AssetOS.WINDOWS
                        ) -> List[str]:
    if not os.path.isfile(f'tmp/manifest/manifest_{assetOS}_{version}.json') or forceReDownload:
        logger.debug("Couldn't find manifest or user requested a new one")
        await ManifestDecoder.getAssetManifestBlocking(version, assetOS)
    if not os.path.isfile(f'tmp/manifest/manifest_{assetOS}_{diffVersion}.json') or forceReDownload:
        logger.debug("Couldn't find manifest or user requested a new one")
        await ManifestDecoder.getAssetManifestBlocking(diffVersion, assetOS)
    async with FileLock.claimFile(os.path.abspath(f'tmp/manifest/manifest_{assetOS}_{version}.json')):
        async with aiofiles.open(f'tmp/manifest/manifest_{assetOS}_{version}.json', 'r') as file:
            content = await file.read()
            newManifest: List[Dict[str, Any]] = json.loads(content)
    async with FileLock.claimFile(os.path.abspath(f'tmp/manifest/manifest_{assetOS}_{diffVersion}.json')):
        async with aiofiles.open(f'tmp/manifest/manifest_{assetOS}_{diffVersion}.json', 'r') as file:
            content = await file.read()
            oldManifest: List[Dict[str, Any]] = json.loads(content)

    return ManifestDiff.compareManifest(newManifest, oldManifest, diffType, prefix)

async def assetGetDiff(version: int, 
                       diffVersion: int, 
                       forceReDownload: bool=False, 
                       diffType: DiffVersion=DiffVersion.ALL, 
                       prefix: str='None', 
                       assetOS: AssetOS=AssetOS.WINDOWS
                       ) -> List[Dict[str, Union[str, List[Dict[str, Union[str, bool]]]]]]:
    if not os.path.isfile(f'tmp/manifest/manifest_{assetOS}_{version}.json') or forceReDownload:
        logger.debug("Couldn't find manifest or user requested a new one")
        await ManifestDecoder.getAssetManifestBlocking(version, assetOS)
    if not os.path.isfile(f'tmp/manifest/manifest_{assetOS}_{diffVersion}.json') or forceReDownload:
        logger.debug("Couldn't find manifest or user requested a new one")
        await ManifestDecoder.getAssetManifestBlocking(diffVersion, assetOS)
    async with FileLock.claimFile(os.path.abspath(f'tmp/manifest/manifest_{assetOS}_{version}.json')):
        async with aiofiles.open(f'tmp/manifest/manifest_{assetOS}_{version}.json', 'r') as file:
            content = await file.read()
            newManifest: List[Dict[str, Any]] = json.loads(content)
    async with FileLock.claimFile(os.path.abspath(f'tmp/manifest/manifest_{assetOS}_{diffVersion}.json')):
        async with aiofiles.open(f'tmp/manifest/manifest_{assetOS}_{diffVersion}.json', 'r') as file:
            content = await file.read()
            oldManifest: List[Dict[str, Any]] = json.loads(content)
    
    newAssets = ManifestDiff.compareManifest(newManifest, oldManifest, diffType, prefix)

    match assetOS:
        case 1:
            assetPath = 'tmp/bundles/android/{}{}'
        case 2:
            assetPath = 'tmp/bundles/ios/{}{}'
        case _:
            assetPath = 'tmp/bundles/windows/{}{}'
            
    response = []
    for assetName in newAssets:
        match assetName.split('_')[0]:
            case 'audio':
                assetExtension = '.wwpkg'
            case _:
                assetExtension = '.bundle'

        asset_path = assetPath.format(assetName, assetExtension)

        if not os.path.isfile(asset_path) or forceReDownload:
            logger.debug(f'Downloading {assetName}{assetExtension}')
            await RequestManager.getSaveAsset(assetName+assetExtension, version, asset_path)

        try:
            response.append({"assetName": assetName, "assetData": await Texture2DDecoder.decodeManyAssets(asset_path)})
        except Exception as e:
            logger.exception(f"Failed to decode asset {assetName}: {e}")
            response.append({"error": str(e)})
    
    return response

async def getAssetBundle(bundleName: str,
                         version: int, 
                         forceReDownload: bool=False, 
                         assetOS: AssetOS=AssetOS.WINDOWS
                         ) -> FileResponse:
    match assetOS:
        case 1:
            bundlePathFormat = 'tmp/bundles/android/{}{}'
        case 2:
            bundlePathFormat = 'tmp/bundles/ios/{}{}'
        case _:
            bundlePathFormat = 'tmp/bundles/windows/{}{}'
    
    match bundleName.split('_')[0]:
            case 'audio':
                assetExtension = '.wwpkg'
            case _:
                assetExtension = '.bundle'

    bundlePath = bundlePathFormat.format(bundleName, assetExtension)

    if not os.path.isfile(bundlePath) or forceReDownload:
        logger.debug(f'Downloading {bundleName}{assetExtension}')
        await RequestManager.getSaveAsset(bundleName + assetExtension, version, bundlePath)
    
    async with FileLock.claimFile(os.path.abspath(bundlePath)):
        async with aiofiles.open(os.path.abspath(bundlePath), "rb") as file:
            content = await file.read()

    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{bundleName}{assetExtension}"'
        }
    )