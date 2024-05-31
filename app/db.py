from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound

from models import Base, User, Song

class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, user_name: str, p_pic) -> User:
        """
        add user to db
        """
        user_info = {"email":email, "user_name":user_name, "p_pic":p_pic}
        user = self.find_item(User, **user_info)
        if user is None:
            user = User(email=email, user_name=user_name, p_pic=p_pic)
            self._session.add(user)
            self._session.commit()
        else:
            self.update_user(user.id, **user_info)
        return user

    def add_song(self, user, **kwargs):
        song = self.find_item(Song, **kwargs)
        if song is None:
            song = Song(**kwargs)
        self._session.add(song)
        if song not in user.songs:
            user.songs.append(song)
        self._session.commit()
        return song
    
    def add_song_to_user(self, song, user):
        user.songs.append(song)
        self._session.commit()

    def find_item(self, model, **kwargs) -> User:
        """
        find user given attributes
        """
        if kwargs is None:
            raise InvalidRequestError
        column_names = model.__table__.columns.keys()
        for key in kwargs.keys():
            if key not in column_names:
                raise InvalidRequestError
        item = self._session.query(model).filter_by(**kwargs).first()
        if item is None:
            return None
        return item

    def update_user(self, id, **kwargs) -> None:
        """
        updates user based on given user_id and
        data to update
        """
        user = self.find_item(User, id=id)
        for key, value in kwargs.items():
            if key not in user.__table__.columns.keys():
                raise ValueError
            setattr(user, key, value)
            self._session.commit()

    def get_user_song_uris(self, user):
        songs = user.songs
        song_uris = [song.song_uri for song in songs]
        return song_uris
    
    def remove_all_songs_from_user(self, user):
        user.songs.clear()
        self._session.commit()