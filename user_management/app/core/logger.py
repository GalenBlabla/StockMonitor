import logging
from app.config import settings

def setup_logging():
    logging.getLogger('pika').setLevel(logging.WARNING)
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
