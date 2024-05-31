from sqlalchemy import Column, String, Integer, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


association_table = Table('association', Base.metadata,
                          Column('user_id', ForeignKey('user.id'), primary_key=True),
                          Column('song_id', ForeignKey('song.id'), primary_key=True))
class User(Base):
    """
    Declare a table called users
    """
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    user_name = Column(String, nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    p_pic = Column(String, nullable=True)

    songs = relationship("Song",
                    secondary=association_table,
                    back_populates="users")

class Song(Base):
    """
    A table for song
    """
    __tablename__ = "song"
    id = Column(Integer, primary_key=True)
    song_name = Column(String)
    image_url = Column(String)
    link = Column(String)
    song_uri = Column(String, unique=True)

    users = relationship("User",
                    secondary=association_table,
                    back_populates="songs")
