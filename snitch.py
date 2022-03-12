import logging

log_file_path = "snitch.log"
logging.basicConfig(filename=log_file_path,
                    format="%(levelname)s - %(asctime)s - %(message)s",
                    filemode="w")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
