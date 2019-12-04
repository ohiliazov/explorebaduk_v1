import logging

logging.basicConfig(level=logging.INFO)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(module)s %(funcName)s] %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
stream_handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(stream_handler)
