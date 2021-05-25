import logging

logger = logging.getLogger("explorebaduk")
logger.propagate = False
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setFormatter(
    logging.Formatter(
        fmt="%(asctime)s : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ),
)
logger.addHandler(ch)
