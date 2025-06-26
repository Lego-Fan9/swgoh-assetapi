from enum import Enum

class AssetOS(int, Enum):
    WINDOWS = 0
    ANDROID = 1
    IOS = 2

class DiffVersion(int, Enum):
    ALL = 0
    NEW = 1
    CHANGED = 2

class Swagger:
    versionDesc = 'Asset version to download from. You can get this from Comlink /metadata or set this to 0 to pull from Comlink if you have that configured.'
    assetNameDesc = 'The name of the asset you want. Get it from /Asset/list.'
    forceReDownloadDesc = 'If true it will download fresh assets for everything.'
    assetOSDesc = 'Choose what version of the asset you want. 0 is Windows, 1 is Android, 2 is iOS. Windows is biggest Android is smallest.'
    assetNamesDesc = 'The names of all the assets you wanted seperated by a comma. Get asset names from /Asset/list'
    diffVersionDesc = 'The version you want to compare to. Usually this should be older.'
    diffTypeDesc = 'Limit how assets are decided as different. New assets = 1, changed = 2, both = 0.'
    prefixDesc = 'Limit to specific prefixes such as charui'