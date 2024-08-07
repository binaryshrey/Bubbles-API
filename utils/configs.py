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