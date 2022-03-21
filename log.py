import logging

logging.basicConfig(filename="snitch.log", filemode="w", format = "[%(levelname)s] - %(asctime)s - %(message)s")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
