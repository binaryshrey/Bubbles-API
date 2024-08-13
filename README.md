# Bubbles API ![Render deployments](https://img.shields.io/github/deployments/binaryshrey/bubbles/production?style=flat&logo=render&label=render) ![BetterStack deployments](https://img.shields.io/github/deployments/binaryshrey/bubbles/production?style=flat&logo=betterstack&label=betterstack) ![supabase](https://img.shields.io/github/deployments/binaryshrey/bubbles/production?style=flat&logo=supabase&label=supabase) ![Upstash-redis](https://img.shields.io/github/deployments/binaryshrey/bubbles/production?style=flat&logo=upstash&label=upstash)
FastAPI service powering Bubbles app

## Getting Started

1. Activate virtual-env
```zsh
cd Bubbles-API
python3 -m venv  bubbles-api-env
.  bubbles-api-env/bin/activate
```

2. Install dependencies
```zsh
pip install -r requirements.txt
```

3. Start server
```zsh
uvicorn main:app --reload
```

4. Open API docs
```zsh
http://127.0.0.1:8000/v1/documentation
```

## Configs
- Connect and enable Firebase-Storage
- Connect and enable Supabase-PostgreSQL
- Connect and enable Upstash-Redis
- Create a .env file for Supabase-PostgreSQL, Firebase-Storage Admin, Upstash-Redis
```
DB_HOST=****-****
DB_NAME=****-****
DB_PASSWORD=****-****
DB_USERNAME=****-****

REDIS_HOST=****-****
REDIS_PASSWORD=****-****
REDIS_PORT=****-****
REDIS_USER=****-****
REDIS_URL=****-****

TYPE=****-****
PROJECT_ID=****-****
PRIVATE_KEY_ID=****-****
PRIVATE_KEY=****-****
CLIENT_EMAIL=****-****
CLIENT_ID=****-****
AUTH_URI=****-****
TOKEN_URI=****-****
AUTH_PROVIDER_X509_CERT_URL=****-****
CLIENT_X509_CERT_URL=****-****
UNIVERSE_DOMAIN=****-****

FIREBASE_CLOUD_STORAGE_BUCKET=****-****
BUBBLE_LINK_EXPIRATION_MIN=****-****

```

