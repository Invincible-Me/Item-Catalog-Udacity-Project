import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    image = Column(String(250))

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id
        }


class MovieDB(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    movieName = Column(String(250), nullable=False)
    posterUrl = Column(String(800), nullable=False)
    genre = Column(String(), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.movieName,
            'genre': self.genre,
            'posterUrl': self.posterUrl
        }


engine = create_engine('sqlite:///movieinfo.db')
Base.metadata.create_all(engine)
