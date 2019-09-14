from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from movieinfo import *

engine = create_engine('sqlite:///movieinfo.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
User1 = User(name="Raunak Singh",
             email="invincibleme.404@gmail.com")
session.add(User1)
session.commit()

# Dummy books data
movie1 = movieDB(movieName="Bahubali",
                 posterUrl="""https://m.media-amazon.com/images/M/MV5BYWVlMjVhZWYtNWViNC00ODFkLTk1MmItYjU1MDY5ZDdhMTU3XkEyXkFqcGdeQXVyODIwMDI1NjM@._V1_UX182_CR0,0,182,268_AL__QL50.jpg""",
                 genre="Action",
                 user_id=1)

session.add(movie1)
session.commit()

movie2 = movieDB(movieName="3 Idiots",
                 posterUrl="""https://m.media-amazon.com/images/M/MV5BNTkyOGVjMGEtNmQzZi00NzFlLTlhOWQtODYyMDc2ZGJmYzFhXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_UY268_CR2,0,182,268_AL__QL50.jpg""",
                 genre="Comedy",
                 user_id=1)

session.add(movie2)
session.commit()

movie3 = movieDB(movieName="Avengers",
                 posterUrl="""https://m.media-amazon.com/images/M/MV5BMTc5MDE2ODcwNV5BMl5BanBnXkFtZTgwMzI2NzQ2NzM@._V1_UX182_CR0,0,182,268_AL__QL50.jpg""",
                 genre="Sci-Fi",
                 user_id=1)

session.add(movie3)
session.commit()

movie4 = movieDB(movieName="Avatar",
                 posterUrl="""https://m.media-amazon.com/images/M/MV5BMTYwOTEwNjAzMl5BMl5BanBnXkFtZTcwODc5MTUwMw@@._V1_UX182_CR0,0,182,268_AL__QL50.jpg""",
                 genre="Fantasy",
                 user_id=1)

session.add(movie4)
session.commit()


print "The page is Fake !"
