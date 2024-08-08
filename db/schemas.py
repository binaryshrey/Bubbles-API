from pydantic import BaseModel, Field
from typing import List


class BubbleLink(BaseModel):
    link_id: str = Field(min_length=1, max_length=100)
    user_id: str = Field(min_length=1, max_length=100)
    user_email: str = Field(min_length=1, max_length=100)
    album_id: str = Field(min_length=1, max_length=100)
    album_name: str = Field(min_length=1, max_length=100)
    album_photos: List[str]

    # Default config override
    class Config:
        json_schema_extra = {
            'example': {
                "link_id": "e4c12048-f296-4199-b619-d32bb8c22zz026",
                "user_id": "a15aea38",
                "user_email": "hello@bubbles-inc.com",
                "album_id": "hello@bubbles-inc.com:e4c12048-f296-4199-b619-d32bb8c22zz026",
                "album_name": "Hello Bubbles",
                "album_photos": ["https://images.unsplash.com/photo-1655321300721-5debfd81176b","https://images.unsplash.com/photo-1655321300721-5debfd81176b"]

            }
        }




class BubbleLinkExpiry(BaseModel):
    user_email: str = Field(min_length=1, max_length=100)

    # Default config override
    class Config:
        json_schema_extra = {
            'example': {
                "user_email": "hello@bubbles-inc.com",
            }
        }


class BubbleLinkPermission(BaseModel):
    link_id: str = Field(min_length=1, max_length=100)
    ip_address: str = Field(min_length=1, max_length=100)

    # Default config override
    class Config:
        json_schema_extra = {
            'example': {
                "link_id": "e4c12048-f296-4199-b619-d32bb8c22zz026",
                "ip_address": "112.98.107.32",
            }
        }