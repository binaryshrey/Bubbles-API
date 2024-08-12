########################################################################### - Imports - ###########################################################################

from db import models
from slowapi import Limiter
from db.database import engine
from collections import Counter
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging, aioredis, json, firebase_admin
from firebase_admin import credentials, storage
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, Security, Request, HTTPException
from db.schemas import BubbleLink, BubbleUser, BubbleLinkPermission
from utils.utility import rate_limit_exceeded_handler, get_db, CustomUnAuthException, get_referrer
from utils.configs import BUBBLE_LINK_EXPIRATION_MIN, REDIS_URL, SERVICE_ACCOUNT_KEY, FIREBASE_CLOUD_STORAGE_BUCKET

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
firebase_cloud_storage_bucket = None


# enable CORS
origins = [
    "https://bubbles-inc.vercel.app",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# On-Start
@app.on_event("startup")
async def startup_event():
    # connect to Redis on startup
    app.state.redis = await aioredis.create_redis_pool(f"{REDIS_URL}")
    logger.info("Connected to Redis")

    # initialize firebase-admin-sdk & cloud-storage-bucket
    firebase_admin.initialize_app(credentials.Certificate(SERVICE_ACCOUNT_KEY), {
        'storageBucket': FIREBASE_CLOUD_STORAGE_BUCKET
    })
    global firebase_cloud_storage_bucket
    firebase_cloud_storage_bucket = storage.bucket()
    logger.info("Connected to Firebase Cloud Storage Bucket")


# On-Destroy
@app.on_event("shutdown")
async def shutdown_event():
    # disconnect from Redis on shutdown
    app.state.redis.close()
    await app.state.redis.wait_closed()
    logger.info("Disconnected from Redis")

    # disconnect from cloud-storage-bucket
    global firebase_cloud_storage_bucket
    firebase_cloud_storage_bucket = None
    logger.info("Disconnected from Firebase Cloud Storage Bucket")


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
@app.post('/add-link', status_code=201)
@limiter.limit('10/minute')
async def add_bubble_link(request: Request, bubbleLink: BubbleLink, db: Session = Depends(get_db)):
    try:
        new_link = models.BubblesEntity()
        new_link.link_id = bubbleLink.link_id
        new_link.user_id = bubbleLink.user_id
        new_link.user_email = bubbleLink.user_email
        new_link.album_id = bubbleLink.album_id
        new_link.album_name = bubbleLink.album_name
        new_link.album_photos = bubbleLink.album_photos
        new_link.created_at = bubbleLink.created_at
        new_link.expires_at = (datetime.strptime(bubbleLink.created_at, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=int(BUBBLE_LINK_EXPIRATION_MIN))).strftime("%Y-%m-%d %H:%M:%S")
        new_link.is_active = True
        new_link.viewed_by = []
        new_link.link_analytics = []
        db.add(new_link)
        db.commit()

        # save-to-redis
        await app.state.redis.set(f"{bubbleLink.user_email}:{bubbleLink.link_id}", json.dumps({'expires_at': (datetime.now() + timedelta(minutes=int(BUBBLE_LINK_EXPIRATION_MIN))).strftime("%Y-%m-%d %H:%M:%S")}))
        await app.state.redis.expire(f"{bubbleLink.user_email}:{bubbleLink.link_id}", 24 * 60 * 60)

        logger.info(f"New link record created by - {bubbleLink.user_email}")
        return {'message': f'New link record created by - {bubbleLink.user_email}'}

    except Exception as e:
        logger.warning(f"Error adding link created by - {bubbleLink.user_email} : {e}")
        raise CustomUnAuthException(detail="Internal Server Error")


# get-albums
@app.get('/get-albums', status_code=200)
@limiter.limit('100/minute')
async def get_albums(request: Request, user_email: str = '',  db: Session = Depends(get_db)):
    try:
        if user_email:
            user_albums = db.query(models.BubblesEntity).filter(models.BubblesEntity.user_email == user_email).all()
            albums_list = [{'link_id': album.link_id, 'user_id': album.user_id, 'user_email': album.user_email, 'album_id': album.album_id, 'album_name': album.album_name, 'album_photos': album.album_photos, 'is_active': album.is_active, 'created_at': album.created_at, 'expires_at': album.expires_at, 'viewed_by': album.viewed_by, 'link_analytics': album.link_analytics} for album in user_albums]
            sources = ["web", "twitter", "whatsapp", "fb", "reddit", "telegram", "gmail"]
            albums_about_to_expire = []
            for album in albums_list:
                if datetime.strptime(album['created_at'], "%Y-%m-%d %H:%M:%S") + timedelta(minutes=3) <= datetime.now() <= datetime.strptime(album['expires_at'], "%Y-%m-%d %H:%M:%S"):
                    albums_about_to_expire.append(album['album_name'])
                count_data = Counter(item['referred_by'] for item in album['link_analytics'])
                analytics = [{"source": source, "visits": count_data.get(source, 0)} for source in sources]
                album['analytics'] = analytics

            return {'albums': albums_list, 'albums_expiring': albums_about_to_expire}
        return {'albums': [], 'links_expiring': []}

    except Exception as e:
        logger.warning(f"Error getting albums  - {user_email} : {e}")
        raise CustomUnAuthException(detail="Internal Server Error")


# 2-min link expiry warning
@app.post('/warn-expiry', status_code=200)
@limiter.limit('10/minute')
async def bubble_link_warn_expiry(request: Request, bubbleUser: BubbleUser, db: Session = Depends(get_db)):
    try:
        bubble_user_links = db.query(models.BubblesEntity).filter(models.BubblesEntity.user_email == bubbleUser.user_email)
        links_about_to_expire = []
        for link in bubble_user_links:
            if datetime.strptime(link.created_at, "%Y-%m-%d %H:%M:%S")+timedelta(minutes=3) <= datetime.now() <= datetime.strptime(link.expires_at, "%Y-%m-%d %H:%M:%S"):
                links_about_to_expire.append(link.album_name)

        logger.info(f'Links about to expire for : {bubbleUser.user_email} - {links_about_to_expire}')
        return {'message': f'Links about to expire - {links_about_to_expire}'}

    except Exception as e:
        logger.warning(f"Error getting link expiry warning for - {bubbleUser.user_email} : {e}")
        raise CustomUnAuthException(detail="Internal Server Error")


# check for view permission
@app.put('/check-view-permission')
@limiter.limit('100/minute')
async def bubble_link_view_permission(request: Request, bubbleLinkPermission: BubbleLinkPermission, ref: str = '', db: Session = Depends(get_db)):
    try:
        bubble_link = db.query(models.BubblesEntity).filter(models.BubblesEntity.link_id == bubbleLinkPermission.link_id).first()
        if bubble_link:
            if bubble_link.is_active and bubbleLinkPermission.ip_address not in bubble_link.viewed_by:
                bubble_link.viewed_by = bubble_link.viewed_by + [bubbleLinkPermission.ip_address]
                bubble_link.link_analytics = bubble_link.link_analytics + [{"referred_by": get_referrer(ref), "viewed_at": datetime.now().strftime("%Y-%m-%d %H:%M")}]
                db.commit()
                content = {
                    'user_email': bubble_link.user_email,
                    'album_name': bubble_link.album_name,
                    'album_photos': bubble_link.album_photos,
                    'album_id': bubble_link.album_id,
                    'created_at': bubble_link.created_at,
                    'is_active': bubble_link.is_active,
                    'link_analytics': bubble_link.link_analytics
                }
                return {'message': True, 'contents': content}
            else:
                return {'message': False, 'contents': {}}
        return {'message': False, 'contents': {}}

    except Exception as e:
        logger.warning(f"Error getting view permission for - {bubbleLinkPermission.link_id} : {e}")
        raise CustomUnAuthException(detail="Internal Server Error")


# check for expired albums from redis and remove from firebase-cloud-storage
@app.get('/check-expired-albums')
@limiter.limit('10/minute')
async def bubble_link_check_album_expiry(request: Request, db: Session = Depends(get_db)):
    try:
        redis_keys = await app.state.redis.keys('*')
        for key in redis_keys:
            expires_at = await app.state.redis.get(key)
            if expires_at is not None:
                expires_at_json = json.loads(expires_at).get("expires_at")
                if datetime.now() > datetime.strptime(expires_at_json, "%Y-%m-%d %H:%M:%S"):
                    folder_path = key.decode('utf-8')
                    blobs = firebase_cloud_storage_bucket.list_blobs(prefix=f'{folder_path}/')
                    for blob in blobs:
                        blob.delete()
                    logger.info(f'Deleted expired firebase cloud album folder : {folder_path}')
                    await app.state.redis.delete(folder_path)
                    logger.info(f'Deleted expired redis key : {folder_path}')

                    # set is_active_link to false in DB
                    bubble_link = db.query(models.BubblesEntity).filter(models.BubblesEntity.album_id == key.decode('utf-8')).first()
                    bubble_link.is_active = False
                    db.commit()
                    logger.info(f'Bubble link expired in DB: {key}')

                    return {'message': 'Deleted Expired Cloud Albums'}

        return {'message': 'No expired cloud albums found'}

    except Exception as e:
        logger.warning(f"Error while checking for expired links : {e}")
        raise CustomUnAuthException(detail="Internal Server Error")


# analytics-overview
@app.get('/analytics-overview', status_code=200)
@limiter.limit('100/minute')
async def analytics_overview(request: Request, user_email: str = '', db: Session = Depends(get_db)):
    try:
        bubble_user_albums = db.query(models.BubblesEntity).filter(models.BubblesEntity.user_email == user_email).all()
        if bubble_user_albums:
            live_albums = 0
            total_album_views = 0
            sources = []
            top_traffic_source = ""
            for album in bubble_user_albums:
                if album.is_active:
                    live_albums = live_albums + 1
                total_album_views = total_album_views + len(album.viewed_by)
                sources = sources + album.link_analytics

            referred_sources = [source['referred_by'] for source in sources]
            frequency = Counter(referred_sources)
            max_frequency = max(frequency.values())
            max_referrers = [referer for referer, count in frequency.items() if count == max_frequency]
            for referer in max_referrers:
                top_traffic_source = referer

            analytics = {
                "total_albums": len(bubble_user_albums),
                "live_albums": live_albums,
                "total_album_views": total_album_views,
                "top_traffic_source": top_traffic_source
            }

            return {'analytics': analytics}
        return {'analytics': {
                "total_albums": 0,
                "live_albums": 0,
                "total_album_views": 0,
                "top_traffic_source": 'no source'
            }}

    except Exception as e:
        logger.warning(f"Error getting analytics for - {user_email} : {e}")
        raise CustomUnAuthException(detail="Internal Server Error")


# delete albums
@app.delete('/delete-albums', status_code=200)
@limiter.limit('10/minute')
async def bubble_link_warn_expiry(request: Request, user_email: str = '', db: Session = Depends(get_db)):
    try:
        bubble_user_albums = db.query(models.BubblesEntity).filter(models.BubblesEntity.user_email == user_email).all()
        if bubble_user_albums:
            for album in bubble_user_albums:
                db.delete(album)
            db.commit()
            logger.info(f"All Bubbles Albums Deleted Successfully - {user_email}")
            return {"message": "All Bubbles Albums Deleted Successfully!"}

        logger.info(f"No Bubbles Albums Found To Be Deleted - {user_email}")
        return {"message": "No Bubbles Albums Found To Be Deleted."}

    except Exception as e:
        logger.warning(f"Error deleting bubbles albums - {user_email} : {e}")
        raise CustomUnAuthException(detail="Internal Server Error")