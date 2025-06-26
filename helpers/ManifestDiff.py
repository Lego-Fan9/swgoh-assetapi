from typing import Dict, List, Any
from helpers.TypeHelpers import DiffVersion

def compareManifest(newManifestFull: List[Dict[str, Any]], 
                    oldManifestFull: List[Dict[str, Any]], 
                    type: DiffVersion=DiffVersion.ALL, 
                    prefix: str='None'
                    ) -> List[str]:
    
    newManifest: List[Dict[str, Any]] = []
    oldManifest: List[Dict[str, Any]] = []

    if prefix != 'None':
        for key in range(len(oldManifestFull)):
            if oldManifestFull[key]['prefix'] == prefix:
                oldManifest.append(oldManifestFull[key])
        for key in range(len(newManifestFull)):
            if newManifestFull[key]['prefix'] == prefix:
                newManifest.append(newManifestFull[key])
    else:
        newManifest = newManifestFull
        oldManifest = oldManifestFull

    match type:
        case 1:
            return checkForNew(newManifest, oldManifest)
        case 2:
            return checkForChange(newManifest, oldManifest)
        case _:
            return checkForNew(newManifest, oldManifest) + checkForChange(newManifest, oldManifest)

def checkForNew(newManifest: List[Dict[str, Any]], 
                oldManifest: List[Dict[str, Any]]
                ) -> List[str]:
    oldNames = []
    for object in oldManifest:
        oldNames.append(object['name'])

    response: List[str] = []
    for key in range(len(newManifest)):
        if not newManifest[key]['name'] in oldNames:
            response.append(newManifest[key]['name'])

    return response

def checkForChange(newManifest: List[Dict[str, Any]], 
                   oldManifest: List[Dict[str, Any]]
                   ) -> List[str]:
    oldVersions = []
    for object in oldManifest:
        oldVersions.append({"name": object['name'], "version": object["version"]})
    
    oldNames = []
    for object in oldManifest:
        oldNames.append(object['name'])

    response: List[str] = []
    for key in range(len(newManifest)):
        if newManifest[key]['name'] in oldNames:
            version = 'Null'
            for object in oldVersions:
                if object["name"] == newManifest[key]['name']:
                    version = object["version"]
                    break
            if version == 'Null':
                raise KeyError('Could not find object["name"] in checkForChange()')
            if newManifest[key]['version'] != version:
                response.append(newManifest[key]['name'])

    return response