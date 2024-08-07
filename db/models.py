from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import ARRAY


class BubblesEntity(Base):
    __tablename__ = "bubbles"

    link_id = Column(String, primary_key=True, unique=True)
    user_id = Column(String)
    user_email = Column(String)
    album_id = Column(String)
    album_name = Column(String)
    album_photos = Column(ARRAY(String))
    created_at = Column(String)
    expires_at = Column(String)
    viewed_by = Column(ARRAY(String))
    viewed_at = Column(ARRAY(String))


