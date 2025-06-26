from typing import Dict
import asyncio

class FileLock:
    def __init__(self):
        self.KeyStore: Dict[str, asyncio.Lock] = {}
    
    def claimFile(self, filepath: str) -> asyncio.Lock:
        if not filepath in self.KeyStore:
            self.KeyStore[filepath] = asyncio.Lock()
            
        return self.KeyStore[filepath]
    
    def checkFileInFileLock(self, filepath: str) -> bool:
        if filepath in self.KeyStore:
            return True
        return False
    
    def cleanFileLock(self):
        for key in list(self.KeyStore.keys()):
            if not self.KeyStore[key].locked():
                del self.KeyStore[key]

GlobalFileLock = FileLock()