import os
from dotenv import load_dotenv

dotenv_path = ".env"
load_dotenv(dotenv_path)


class Env:
    def __init__(self):
        for key, value in os.environ.items():
            setattr(self, key, value)


env = Env()

minerpool_private_key = os.getenv("PRIVATEKEY")
if minerpool_private_key is None:
    print(
        "Validator PRIVATEKEY not found. Please check readme.md to set the PRIVATEKEY in the .env variable."
    )
    exit(0)


# MinerPool Configuration settings
PRIVATEKEY = env.PRIVATEKEY
