from fastapi import FastAPI, Request, HTTPException, Response, Query
from fastapi.responses import HTMLResponse
from helpers import HMACDecoder, Endpoints, FileCleaner, Logger
from helpers.RequestManager import RequestManager
from helpers.TypeHelpers import AssetOS, DiffVersion, Swagger
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from typing import Dict, List, Union, Annotated
import aiofiles
import os

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await RequestManager.httpClient.aclose()

app = FastAPI(lifespan=lifespan, title='SWGoH AssetAPI', description='Download 2D assets from SWGoH', docs_url='/swagger')
HMAC_helper = HMACDecoder.HMACHelper()
logger = Logger.getLogger('assetapi')

COMLINK_SECRET = os.getenv('COMLINK_SECRET', 'False')
COMLINK_PUBLIC = os.getenv('COMLINK_PUBLIC', 'False')
COMLINK_URL = os.getenv('COMLINK_URL', 'False')

if COMLINK_URL == 'False':
    logger.info('No comlink was specified, version=0 is not valid')

@app.get('/')
@app.get('/docs')
async def docsEndpoint() -> HTMLResponse:
    async with aiofiles.open("README.html", "r") as file:
        return HTMLResponse(content=await file.read())

@app.get("/cleanup")
async def cleanupEndpoint() -> Dict[str, str]:
    await FileCleaner.cleanup(os.path.abspath('tmp'))
    return {"status": "done"}

@app.get('/Asset/single')
async def assetSingleAssetEndpoint(request: Request, 
                                   version: Annotated[int, Query(description=Swagger.versionDesc)], 
                                   assetName: Annotated[str, Query(description=Swagger.assetNameDesc)], 
                                   forceReDownload: Annotated[bool, Query(description=Swagger.forceReDownloadDesc)]=False, 
                                   assetOS: Annotated[AssetOS, Query(description=Swagger.assetOSDesc)]=AssetOS.WINDOWS
                                   ) -> Response:
    if not HMAC_helper.verifyHMACRequest(request.headers, request.url.path, b'GET'):
        raise HTTPException(status_code=401, detail="Invalid or missing signature and or timestamp")
    
    if version == 0 and COMLINK_URL != 'False':
        versionFinal = await RequestManager.getAssetVersion(COMLINK_URL, secret_key=COMLINK_SECRET, access_key=COMLINK_PUBLIC)
        logger.info(f'Got assetVersion of {versionFinal} from comlink')
    else:
        versionFinal = version

    return await Endpoints.assetSingle(versionFinal, assetName, forceReDownload, assetOS)

@app.get('/Asset/many')
async def assetManyEndpoint(request: Request, 
                            version: Annotated[int, Query(description=Swagger.versionDesc)], 
                            assetNames: Annotated[str, Query(description=Swagger.assetNamesDesc)], 
                            forceReDownload: Annotated[bool, Query(description=Swagger.forceReDownloadDesc)]=False, 
                            assetOS: Annotated[AssetOS, Query(description=Swagger.assetOSDesc)]=AssetOS.WINDOWS
                            ) -> List[Dict[str, Union[str, List[Dict[str, Union[str, bool]]]]]]:
    if not HMAC_helper.verifyHMACRequest(request.headers, request.url.path, b'GET'):
        raise HTTPException(status_code=401, detail="Invalid or missing signature and or timestamp")
    
    if version == 0 and COMLINK_URL != 'False':
        versionFinal = await RequestManager.getAssetVersion(COMLINK_URL, secret_key=COMLINK_SECRET, access_key=COMLINK_PUBLIC)
        logger.info(f'Got assetVersion of {versionFinal} from comlink')
    else:
        versionFinal = version

    return await Endpoints.assetMany(versionFinal, assetNames, forceReDownload, assetOS)

@app.get('/Asset/list')
async def getManifestEndpoint(request: Request, 
                              version: Annotated[int, Query(description=Swagger.versionDesc)], 
                              forceReDownload: Annotated[bool, Query(description=Swagger.forceReDownloadDesc)]=False, 
                              assetOS: Annotated[AssetOS, Query(description=Swagger.assetOSDesc)]=AssetOS.WINDOWS
                              ) -> List[str]:
    if not HMAC_helper.verifyHMACRequest(request.headers, request.url.path, b'GET'):
        raise HTTPException(status_code=401, detail="Invalid or missing signature and or timestamp")
    
    if version == 0 and COMLINK_URL != 'False':
        versionFinal = await RequestManager.getAssetVersion(COMLINK_URL, secret_key=COMLINK_SECRET, access_key=COMLINK_PUBLIC)
        logger.info(f'Got assetVersion of {versionFinal} from comlink')
    else:
        versionFinal = version

    return await Endpoints.assetList(versionFinal, forceReDownload, assetOS)

@app.get('/Asset/listDiff')
async def listDiffEndpoint(request: Request, 
                           version: Annotated[int, Query(description=Swagger.versionDesc)], 
                           diffVersion: Annotated[int, Query(description=Swagger.diffVersionDesc)], 
                           forceReDownload: Annotated[bool, Query(description=Swagger.forceReDownloadDesc)]=False, 
                           diffType: Annotated[DiffVersion, Query(description=Swagger.diffTypeDesc)]=DiffVersion.ALL, 
                           prefix: Annotated[str, Query(description=Swagger.prefixDesc)]='None', 
                           assetOS: Annotated[AssetOS, Query(description=Swagger.assetOSDesc)]=AssetOS.WINDOWS
                           ) -> List[str]:
    if not HMAC_helper.verifyHMACRequest(request.headers, request.url.path, b'GET'):
        raise HTTPException(status_code=401, detail="Invalid or missing signature and or timestamp")
    
    if version == 0 and COMLINK_URL != 'False':
        versionFinal = await RequestManager.getAssetVersion(COMLINK_URL, secret_key=COMLINK_SECRET, access_key=COMLINK_PUBLIC)
        logger.info(f'Got assetVersion of {versionFinal} from comlink')
    else:
        versionFinal = version

    return await Endpoints.assetListDiff(versionFinal, diffVersion, forceReDownload, diffType, prefix, assetOS)

@app.get('/Asset/getDiff')
async def getDiffEndpoint(request: Request, 
                          version: Annotated[int, Query(description=Swagger.versionDesc)], 
                          diffVersion: Annotated[int, Query(description=Swagger.diffVersionDesc)], 
                          forceReDownload: Annotated[bool, Query(description=Swagger.forceReDownloadDesc)]=False, 
                          diffType: Annotated[DiffVersion, Query(description=Swagger.diffTypeDesc)]=DiffVersion.ALL, 
                          prefix: Annotated[str, Query(description=Swagger.prefixDesc)]='None', 
                          assetOS: Annotated[AssetOS, Query(description=Swagger.assetOSDesc)]=AssetOS.WINDOWS
                          ) -> List[Dict[str, Union[str, List[Dict[str, Union[str, bool]]]]]]:
    if not HMAC_helper.verifyHMACRequest(request.headers, request.url.path, b'GET'):
        raise HTTPException(status_code=401, detail="Invalid or missing signature and or timestamp")
    
    if version == 0 and COMLINK_URL != 'False':
        versionFinal = await RequestManager.getAssetVersion(COMLINK_URL, secret_key=COMLINK_SECRET, access_key=COMLINK_PUBLIC)
        logger.info(f'Got assetVersion of {versionFinal} from comlink')
    else:
        versionFinal = version

    return await Endpoints.assetGetDiff(versionFinal, diffVersion, forceReDownload, diffType, prefix, assetOS)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "3300")), log_config=None)
else:
    logger.warning('App is not run as __main__, not starting the uvicorn server. If you are starting with uvicorn cli, this is fine.')