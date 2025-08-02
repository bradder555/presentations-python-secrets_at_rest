import os

import asyncio

from app import App
from models import Config
from util import SecretUtil

import logging
from systemd.journal import JournaldLogHandler

SERVICE_NAME = "AuroraNotify"
CONFIG_FILE = "./aurora.conf"
ENCR_CONFIG_FILE = "./aurora.dat"

logger = logging.getLogger(SERVICE_NAME)
logger.addHandler(JournaldLogHandler())


if __name__ == "__main__":
    secret_util = SecretUtil(SERVICE_NAME)

    config = None
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as cf:
            # okay to crash if file is corrupted
            config = Config.model_validate_json(cf.read())
        os.unlink(CONFIG_FILE)
        with open(ENCR_CONFIG_FILE, "wb") as cf:
            cf.write(
                secret_util.encrypt(
                    config.model_dump_json().encode()
                )
            )
    else:
        with open(ENCR_CONFIG_FILE, "rb") as ef:
            config = Config.model_validate_json(
                secret_util.decrypt(
                    ef.read()
                )
            )
    app = App(
        service_name=SERVICE_NAME,
        config=config
    )

    asyncio.run(app.run())