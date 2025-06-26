from typing import List
import asyncio
import os

if __name__ == '__main__':
    from FileLock import GlobalFileLock as FileLock
    import Logger
else:
    from helpers import Logger
    from helpers.FileLock import GlobalFileLock as FileLock

logger = Logger.getLogger('FileCleaner')

def getAllFilePaths(directory: str) -> List[str]:
    filePaths = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            filePaths.append(filepath)
    return filePaths

async def delFile(file: str):
    try:
        logger.info(f'Deleting {file}')
        if FileLock.checkFileInFileLock(file):
            async with FileLock.claimFile(file):
                os.remove(file)
        else:
            os.remove(file)
    except Exception as e:
        logger.error(f'Error deleting file: {file}, {e}')

async def cleanup(filepath: str):
    fileList = getAllFilePaths(filepath)

    try:
        tasks = [asyncio.create_task(delFile(file)) for file in fileList]
        await asyncio.gather(*tasks)
        logger.info(f'Cleaned directory: {filepath}')
    except Exception as e:
        logger.error(f'Failed to clean directory: {filepath}, {e}')
    
    if __name__ != '__main__':
        FileLock.cleanFileLock()
        logger.info('Cleaned FileLock KeyStore')

if __name__ == '__main__':
    asyncio.run(cleanup(os.path.abspath('./tmp')))