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
FIREBASE_CLOUD_STORAGE_BUCKET = env_get("FIREBASE_CLOUD_STORAGE_BUCKET")
SERVICE_ACCOUNT_KEY = {
    "type": env_get("TYPE"),
    "project_id": env_get("PROJECT_ID"),
    "private_key_id": env_get("PRIVATE_KEY_ID"),
    "private_key": env_get("PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": env_get("CLIENT_EMAIL"),
    "client_id": env_get("CLIENT_ID"),
    "auth_uri": env_get("AUTH_URI"),
    "token_uri": env_get("TOKEN_URI"),
    "auth_provider_x509_cert_url": env_get("AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": env_get("CLIENT_X509_CERT_URL"),
    "universe_domain":  env_get("UNIVERSE_DOMAIN")
}