import logging
import logging.config
import os
import yaml
from dotenv import load_dotenv
import time
from decouple import config

logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("faiss.loader").setLevel(logging.ERROR)
load_dotenv()
with open(os.environ.get("LOGGER_CONFIG"), "r") as f:
    config = yaml.safe_load(f)


logging.config.dictConfig(config)
env_logger = os.environ.get("ENVIRONMENT", "development").lower()
logger = logging.getLogger(env_logger)


# TODO[] il logger non funziona correttamente ad oggi 01/03
def log_function_call(func):
    """auto log important info from function call

    Args:
        func (_type_):
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        properties = {
            "custom_dimensions": {
                "func_name": func.__name__,
                "elapsed": end_time - start_time,
                "args": args,
                "kwargs": kwargs,
                "return": result,
            }
        }
        logger.log(
            logging.INFO,
            msg=f"Calling {func.__name__} elapsed: {end_time-start_time}",
            extra=properties,
        )
        return result

    return wrapper
