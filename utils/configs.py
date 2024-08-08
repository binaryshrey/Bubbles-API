import os
from dotenv import load_dotenv


load_dotenv()


def env_get(env_var: str) -> str:
    val = os.environ.get(env_var)
    if not val:
        raise KeyError(f"Env variable '{env_var}' is not set!")
    return val


DB_HOST = env_get("DB_HOST")
DB_NAME = env_get("DB_NAME")
DB_PASSWORD = env_get("DB_PASSWORD")
DB_USERNAME = env_get("DB_USERNAME")
REDIS_HOST = env_get("REDIS_HOST")
REDIS_PASSWORD = env_get("REDIS_PASSWORD")
REDIS_PORT = env_get("REDIS_PORT")
REDIS_URL = env_get("REDIS_URL")
REDIS_USER = env_get("REDIS_USER")
BUBBLE_LINK_EXPIRATION_MIN = env_get("BUBBLE_LINK_EXPIRATION_MIN")