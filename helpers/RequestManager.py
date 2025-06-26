from fastapi import HTTPException
from helpers import Logger
from helpers.FileLock import GlobalFileLock as FileLock
from helpers.TypeHelpers import AssetOS
from typing import Union, Dict, List
import aiofiles
import hashlib
import httpx
import hmac
import json
import time
import os

class request_manager:
    def __init__(self):
        self.logger = Logger.getLogger("requestManager")
        self.httpClient = httpx.AsyncClient()

    async def getAsset(self, 
                       asset: str, 
                       version: int, 
                       assetOS: AssetOS=AssetOS.WINDOWS, 
                       response_type: str="content"
                       ) -> Union[bytes, str, Dict, List, None]:
        match assetOS:
            case 0:
                assetOSPath = "/Windows/ETC/"
            case 1:
                assetOSPath = "/Android/ETC/"
            case 2:
                assetOSPath = "/iOS/PVRTC/"
            case _:
                assetOSPath = "/Windows/ETC/"

        url = "https://eaassets-a.akamaihd.net/assetssw.capitalgames.com/PROD/{}{}{}".format(version, assetOSPath, asset)

        try:
            response = await self.httpClient.get(url)
            if response.status_code == 200:
                match response_type:
                    case "text":
                        return response.text
                    case "json":
                        return response.json()
                    case _:
                        return response.content
                    
            else:
                self.logger.warning(f'Returned status code was "{response.status_code}" expected "200" message is "{response.content}"')
                raise HTTPException(status_code=500, detail=f"Failed to get {asset} from EA server")
            
        except httpx.ConnectError as e:
            self.logger.warning(f'Failed to download {asset}(ConnectionError): {e}')
            raise HTTPException(status_code=500, detail=f"Failed to get {asset} from EA server")
        except httpx.ReadTimeout as e:
            self.logger.warning(f'Failed to download {asset}(Timeout): {e}')
            raise HTTPException(status_code=500, detail=f"Failed to get {asset} from EA server")
        except httpx.RequestError as e:
            self.logger.warning(f'Failed to download {asset}(RequestException): {e}')
            raise HTTPException(status_code=500, detail=f"Failed to get {asset} from EA server")
        
    async def getSaveAsset(self, 
                           asset: str, 
                           version: int, 
                           filepath: str, 
                           assetOS: AssetOS=AssetOS.WINDOWS):
        assetData = await self.getAsset(asset, version, assetOS, response_type="content")

        if not isinstance(assetData, (bytes, bytearray)):
            self.logger.warning(f"Asset data for {asset} is not bytes or str, got {type(assetData)}")
            raise TypeError(f"Asset data for {asset} is not bytes or str, got {type(assetData)}")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        async with FileLock.claimFile(os.path.abspath(filepath)):
            async with aiofiles.open(filepath, 'wb') as file:
                await file.write(assetData)
        
    async def getAssetVersion(self, 
                              url_base: str, 
                              secret_key: str='False', 
                              access_key: str='False', 
                              endpoint: str='metadata', 
                              payload: Dict={}
                              ) -> int:
            # This function is adapted from _post in https://github.com/swgoh-utils/comlink-python
            post_url = url_base + f'/{endpoint}'
            req_headers: Dict[str, str] = {}
            if secret_key != 'False' and access_key != 'False':
                req_time = str(int(time.time() * 1000))
                req_headers = {"X-Date": f'{req_time}'}

                hmac_obj = hmac.new(key=secret_key.encode(), digestmod=hashlib.sha256)
                hmac_obj.update(req_time.encode())
                hmac_obj.update(b'POST')
                hmac_obj.update(f'/{endpoint}'.encode())

                if payload:
                    payload_string = json.dumps(payload, separators=(',', ':'))
                else:
                    payload_string = json.dumps({})

                payload_hash_digest = hashlib.md5(payload_string.encode()).hexdigest()
                hmac_obj.update(payload_hash_digest.encode())
                hmac_digest = hmac_obj.hexdigest()
                
                req_headers['Authorization'] = f'HMAC-SHA256 Credential={access_key},Signature={hmac_digest}'
            try:
                response = await self.httpClient.post(post_url, json=payload, headers=req_headers)

                return json.loads(response.content.decode('utf-8'))['assetVersion']
            except httpx.ConnectError as e:
                self.logger.warning(f'Failed to download version from comlink (ConnectionError): {e}')
                raise HTTPException(status_code=500, detail=f"Failed to get version from comlink")
            except httpx.ReadTimeout as e:
                self.logger.warning(f'Failed to download version from comlink (Timeout): {e}')
                raise HTTPException(status_code=500, detail=f"Failed to get version from comlink")
            except httpx.RequestError as e:
                self.logger.warning(f'Failed to download version from comlink (RequestException): {e}')
                raise HTTPException(status_code=500, detail=f"Failed to get version from comlink")

RequestManager = request_manager()