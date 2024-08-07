########################################################################### - Imports - ###########################################################################

import logging
from db import models
from slowapi import Limiter
from db.database import engine
from db.schemas import BubbleLink, BubbleLinkExpiry
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Depends, Security, Request
from utils.configs import BUBBLE_LINK_EXPIRATION_MIN
from utils.utility import rate_limit_exceeded_handler, get_db, CustomUnAuthException

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
models.Base.metadata.create_all(bind=engine)


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


# addLink
@app.post('/addLink', status_code=201)
@limiter.limit('50/minute')
async def add_bubble_link(request: Request, bubbleLink: BubbleLink, db: Session = Depends(get_db)):
    try:
        new_link = models.BubblesEntity()
        new_link.link_id = bubbleLink.link_id
        new_link.user_id = bubbleLink.user_id
        new_link.user_email = bubbleLink.user_email
        new_link.album_id = bubbleLink.album_id
        new_link.album_name = bubbleLink.album_name
        new_link.album_photos = bubbleLink.album_photos
        new_link.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_link.expires_at = (datetime.now() + timedelta(minutes=int(BUBBLE_LINK_EXPIRATION_MIN))).strftime("%Y-%m-%d %H:%M:%S")
        new_link.viewed_by = []
        new_link.viewed_at = []
        db.add(new_link)
        db.commit()
        logger.info(f"New link record created by - {bubbleLink.user_email}")
        return {'message': f'New link record created by - {bubbleLink.user_email}'}

    except Exception as e:
        logger.warning(f"Error adding link created by - {bubbleLink.user_email} : {e}")
        raise CustomUnAuthException(detail="Internal Server Error")




# 2-min link expiry warning
@app.post('/warn-expiry', status_code=200)
@limiter.limit('100/minute')
async def bubble_link_warn_expiry(request: Request, bubbleLinkExpiry: BubbleLinkExpiry, db: Session = Depends(get_db)):
    try:
        bubble_user_links = db.query(models.BubblesEntity).filter(models.BubblesEntity.user_email == bubbleLinkExpiry.user_email)
        links_about_to_expire = []
        for link in bubble_user_links:
            if datetime.strptime(link.created_at, "%Y-%m-%d %H:%M:%S")+timedelta(minutes=3) <= datetime.now() <= datetime.strptime(link.expires_at, "%Y-%m-%d %H:%M:%S"):
                links_about_to_expire.append(link.album_name)

        logger.info(f'Links about to expire for : {bubbleLinkExpiry.user_email} - {links_about_to_expire}')
        return {'message': f'Links about to expire - {links_about_to_expire}'}

    except Exception as e:
        logger.warning(f"Error getting link expiry warning for - {bubbleLinkExpiry.user_email} : {e}")
        raise CustomUnAuthException(detail="Internal Server Error")


