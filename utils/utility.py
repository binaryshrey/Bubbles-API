from starlette.requests import Request
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse, Response


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    a simple JSON response that includes the details of the rate limit
    that was hit. If no limit is hit, the countdown is added to headers.
    """
    response = JSONResponse(
        {"message": 'Too many requests (Rate limit reached). Please try again in sometime.'}, status_code=200
    )
    response = request.app.state.limiter._inject_headers(response, request.state.view_rate_limit)
    return response
