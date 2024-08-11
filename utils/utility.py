from starlette.requests import Request
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse, Response
from db.database import SessionLocal
import logging
from fastapi import HTTPException, status




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
