########################################################################### - Imports - ###########################################################################

import logging
from slowapi import Limiter
from fastapi import FastAPI, Depends, Security, Request
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from utils.utility import rate_limit_exceeded_handler

########################################################################### - Imports - ###########################################################################




# SETUP LOGGER
logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__file__)




# DNA
app = FastAPI(
    title='Bubbles API-v1',
    description='Bubbles API',
    version='0.1',
    docs_url='/v1/documentation',
    redoc_url='/v1/redoc',
    openapi_url='/v1/openapi.json'
)




# INIT
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)



# root
@app.get("/")
@limiter.limit("5/minute")
async def root(request: Request):
    return {"message": "Hello Bubbles!"}




# health
@app.get('/health')
@limiter.limit("5/minute")
async def check_alive(request: Request):
    return {'message': 'alive'}