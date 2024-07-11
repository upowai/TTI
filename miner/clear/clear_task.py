import os
import shutil
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)


def clear_directory(path):
    try:
        if os.path.isfile(path):
            os.unlink(path)
            logging.info(f"Deleted file: {path}")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            logging.info(f"Deleted directory and its contents: {path}")
        else:
            logging.error(f"Path is neither a file nor a directory: {path}")
    except Exception as e:
        logging.error("Failed to delete %s. Reason: %s", path, e)
