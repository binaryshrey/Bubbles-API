from starlette.requests import Request
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse, Response
from db.database import SessionLocal
import logging
from firebase_admin import auth
from fastapi import HTTPException, status
from fastapi import Depends, HTTPException, Header


class CustomUnAuthException(HTTPException):
    def __init__(self, detail: str):
        self.detail = {
            'message': detail,
        }
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=self.detail
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    a simple JSON response that includes the details of the rate limit
    that was hit. If no limit is hit, the countdown is added to headers.
    """
    response = JSONResponse(
        {"message": 'Too many requests (Rate limit reached). Please try again in sometime.'}, status_code=429
    )
    response = request.app.state.limiter._inject_headers(response, request.state.view_rate_limit)
    return response


def get_referrer(ref):
    logging.info(ref)
    if ref == 'whatsapp':
        return 'whatsapp'
    elif ref == 'twitter':
        return 'twitter'
    elif ref == 'reddit':
        return 'reddit'
    elif ref == 'fb':
        return 'fb'
    elif ref == 'gmail':
        return 'gmail'
    elif ref == 'telegram':
        return 'telegram'
    else:
        return 'web'


async def verify_firebase_token(id_token: str):
    try:
        decoded_token = auth.verify_id_token(id_token)
        logging.info(decoded_token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_current_user(authorization: str = Header(...)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = authorization.split("Bearer ")[-1]
    logging.info(token)
    decoded_token = await verify_firebase_token(token)
    return decoded_token
