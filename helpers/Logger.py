import logging
from logging.handlers import RotatingFileHandler
import sys
import os

LOG_FILE = os.getenv('LOG_FILE', True)
LOG_DIR = os.getenv('LOG_PATH', os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'logs'))

handlers = []
formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class ConsoleFilter(logging.Filter):
    def __init__(self, suppressed_loggers):
        super().__init__()
        self.suppressed_loggers = suppressed_loggers

    def filter(self, record: logging.LogRecord) -> bool:
        if record.name in self.suppressed_loggers and record.levelno < logging.WARNING:
            return False
        return True

console_suppress = ['httpcore.http11', 'httpcore.connection', 'fsspec.local', 'asyncio', 'httpx']

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.addFilter(ConsoleFilter(console_suppress))
handlers.append(console_handler)

if LOG_FILE == True:
    os.makedirs(LOG_DIR, exist_ok=True)
    file_handler = RotatingFileHandler(os.path.join(LOG_DIR, "assetapi.log"), maxBytes=5*1024*1024, backupCount=3)
    file_handler.setFormatter(formatter)
    handlers.append(file_handler)

logging.basicConfig(level=logging.DEBUG, handlers=handlers)

def getLogger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    
    return logger