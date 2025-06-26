# SWGoH AssetAPI

A FastAPI that can download assets for Star Wars: Galaxy of Heroes

This API should work in direct parody with [Asset Extractor 2](https://github.com/swgoh-utils/swgoh-ae2)'s AssetWebApi however I have added some endpoints not present in Asset Extractor 2. This tool also works on ARM64 because it uses UnityPy instead of AssetStudioMod

## Running with Docker

Start the container with something like this:

```
docker pull ghcr.io/lego-fan9/swgoh-assetapi:latest
docker run --name AssetAPI \
    -d \
    -restart always \
    -p 3300:3300 \
    ghcr.io/lego-fan9/swgoh-assetapi:latest
```

## Running without Docker

This tool uses FastAPI with uvicorn so you can do
```
pip install UnityPy httpx python-dotenv protobuf fastapi uvicorn aiofiles
git clone https://github.com/lego-fan9/swgoh-assetapi
cd swgoh-assetapi
python assetapi.py
```

Note: If running in a VM or other compact OS, you may need to install UnityPy from a wheel, or a c/c++ compiler

## Enviroment Variables

* ACCESS_KEY
  * Optional access/public key. If a secret key is also set HMAC signing is enabled.
* SECRET_KEY
  * Optional secret key. If a access key is also set HMAC signing is enabled.
* COMLINK_URL
  * Optional comlink url. If provided you may use automatic comlink asset version getter. See [AssetVersion](#assetversion) for more details
* COMLINK_ACCESS
  * Optional comlink access key. If comlink secret key is also set, your communication with comlink will use HMAC signing
* COMLINK_SECRET
  * Optional comlink secret key. If comlink access key is also set, your communication with comlink will use HMAC signing

See [HMACSigning](#hmacsigning) for more on HMAC signing

## Endpoints

All endpoints are GET.

These docs are avaliable at `/docs`

Swagger docs are avaliable at `/swagger`

### /Asset/list

Returns a list of every asset in the game. 

**Args:**

* version: int
  * See [AssetVersion](#assetversion)
* forceReDownload: bool, Default: False
  * If set to true it will download a new manifest, otherwise it tries to use a locally stored one
* assetOS: int, Default: 0
  * See [AssetOS](#assetos)

**Response:**

* Type: JSON list
* Format: list[str]

**Example**

```
http://localhost:3300/Asset/list?version=36530&forceReDownload=false&assetOS=1
```
Response: 

```
[
  "ability_000_basic",
  "ability_000_special01",
  "ability_50rt_basic",
  ...
]
```
### /Asset/listDiff

Returns a list of new and/or changed assets

**Args:**

* version: int
  * See [AssetVersion](#assetversion)
* diffVersion: int
  * This is the older version. If you do not have it, this endpoint is useless
* forceReDownload: bool, Default: False
  * If set to true it will download a new manifest, otherwise it tries to use a locally stored one
* diffType: int, Default: 0
  * A diffType of 1 will return all manifest entries that are new, a diffType of 2 will return any entries that changed, a diffType of 0 returns both
* prefix: str, Default: Null
  * A filter to make it only return entries with this as the prefix. The prefix is everything before the first underscore, for example, charui_b1 has charui as the prefix
* assetOS: int, Default: 0
  * See [AssetOS](#assetos)

**Response:**

* Type: JSON list
* Format: list[str]

**Example:**

```
http://localhost:3300/Asset/listDiff?version=36528&diffVersion=36530&forceReDownload=false&diffType=1&assetOS=1
```
Response: 

```
[
  "ability_char_beam_tombguardian_aoe_lb1",
  "ability_char_blade_jumpstrike_cx2_lb",
  "ability_char_force_crush_lordvader_aoe_lb2",
  ...
]
```
### /Asset/single

Get a single asset in a ready to download object `/Asset/many` is recommended over this endpoint, however this exists because it matches what [Asset Extractor 2](https://github.com/swgoh-utils/swgoh-ae2) outputs. [Here's why](#assetsinglevsmany)

**Args:**
* version: int
  * See [AssetVersion](#assetversion)
* assetName: string
  * The name of the asset you want. Get this from `/Asset/list`
* forceReDownload: bool, Default: False
  * If set to true it will download a new copy of the asset, otherwise it tries to use a locally stored one
* assetOS: int, Default: 0
  * See [AssetOS](#assetos)

**Response:**

* Type: attachment
* Format: image/png

**Example:**

```
http://localhost:3300/Asset/single?version=36530&assetName=charui_b1&forceReDownload=false&assetOS=1
```

### /Asset/many

Downloads multiple assets at once. I recommend this endpoint instead of `/Asset/single` [Here's why](#assetsinglevsmany)

**Args:**
* version: int
  * See [AssetVersion](#assetversion)
* assetNames: string
  * The name of the assets you want, seperated by a comma. Get this from `/Asset/list` 
* forceReDownload: bool, Default: False
  * If set to true it will download a new copy of the asset, otherwise it tries to use a locally stored one
* assetOS: int, Default: 0
  * See [AssetOS](#assetos)
  
**Response:**

* Type: JSON list
* Format: 
```
[
    {
        "assetName": string,
        "assetData": [
            {
                "name": string,
                "img": string,
                "valid": bool
            }...
        ]
    }...
]
```

**Example:**

```
http://localhost:3300/Asset/many?version=36530&assetNames=charui_b1%2Ccharui_b2&forceReDownload=false&assetOS=1
```

Response: 

```
[
  {
    "assetName": "charui_b1",
    "assetData": [
      {
        "name": "tex.charui_b1",
        "img": "data:image/png;base64,iVBOR...",
        "valid": true
      }
    ]
  },
  {
    "assetName": "charui_b2",
    "assetData": [
      {
        "name": "tex.charui_b2",
        "img": "data:image/png;base64,iVBOR...",
        "valid": true
      }
    ]
  }
]
```

* assetName
  * The name of the asset as it is found in the manifest
* assetData.name
  * The true asset name. This is what the game uses to save the asset to file
* assetData.img
  * The image data as a base64 download link. This can be pasted straight into a browser
* assetData.valid
  * If the asset failed to be decoded this will be false

## AssetVersion

To get the asset version you need a Comlink instance. For more details on that see [Their GitHub Repository](https://GitHub.com/swgoh-utils/swgoh-comlink)

### Using AssetAPI

AssetAPI has the option to include a link to your comlink instance via the COMLINK_URL enviroment variable. If this is specified, you can do version=0 in all of your requests and it will use Comlink

### Without AssetAPI

If you don't want to use AssetAPI's version getter, You can get it by calling `/metadata` with comlink, and then it is "assetVersion"

## AssetOS

The AssetOS is used to determine which quality of object should be returned. The options are:

* 0
  * This is Windows, and is the highest quality, largest image size
* 1
  * This is Android, and is the lowest quality, smallest image size
* 2
  * This is iOS, and is the middle between Android and Windows

## HMACSigning

If the ACCESS_KEY and SECRET_KEY are both set, HMAC signing is enabled. To create HMAC requests you can do something like this

```python
def generateAuthHeaders(secret_key, access_key, endpoint, timestamp):
        req_headers = {"X-Date": timestamp}

        hmac_obj = hmac.new(key=secret_key.encode(), digestmod=hashlib.sha256)
        hmac_obj.update(timestamp.encode())
        hmac_obj.update(b'GET')
        hmac_obj.update(f'/{endpoint}'.encode())

        hmac_digest = hmac_obj.hexdigest()
        req_headers['Authorization'] = f'HMAC-SHA256 Credential={access_key},Signature={hmac_digest}'

        return req_headers

requests.get(url+endpoint+payload, headers=generateAuthHeaders(SECRET_KEY, ACCESS_KEY, endpoint, str(int(time.time() * 1000))))
```

"endpoint" should be something like "/Asset/list"

## Cleaning temp files up

AssetAPI stores a copy of every bundle it downloads, as well as a JSON version of the manifest. It all goes in the `tmp/` directory. To clean it, you can either delete the `tmp/` directory, run the `/cleanup` endpoint, or run the cleanup script. If you delete the `tmp/` directory or run the cleanup script I suggest restarting the server as well. 

To run the cleanup script navigate to the same directory as `assetapi.py` then run `cd helpers`. finally run 
```
python FileCleaner.py
```

## AssetSingleVsMany

* `/Asset/single`
  * Returns a single asset only
* `/Asset/many`
  * Returns many assets, but you need to decode a bit

Unity bundles can contain many assets in them. You can only return a single asset with the method `/Asset/single` uses, even if there are many in a bundle, So `/Asset/single` will return the first image UnityPy finds. `/Asset/many` is able to return many more. To see this for yourself I suggest looking at the results of both of these.

```
http://localhost:3300/Asset/single?version=36530&assetName=shared_resourcecontainer
```

```
http://localhost:3300/Asset/many?version=36530&assetNames=shared_resourcecontainer
```