from flask import Flask, render_template, request, redirect, url_for, \
    flash, jsonify
from flask import session as login_session
from flask import make_response

# importing SqlAlchemy
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from movie_database import *
import random
import string
import httplib2
import json
import requests

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenCredentials

app = Flask(__name__)
app.secret_key="shhhhh"

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item-Catalog"

engine = create_engine('sqlite:///movieinfo.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def check_user():
    email = login_session['email']
    return session.query(User).filter_by(email=email).one_or_none()


# retreive admin user details

def check_admin():
    return session.query(User).filter_by(
        email='invincibleme.404@gmail.com').one_or_none()


# Add new user into database

def createUser():
    name = login_session['name']
    email = login_session['email']
    url = login_session['img']
    provider = login_session['provider']
    newUser = User(name=name, email=email, image=url, provider=provider)
    session.add(newUser)
    session.commit()


def new_state():
    state = ''.join(random.choice(string.ascii_uppercase +
                                  string.digits) for x in xrange(32))
    login_session['state'] = state
    return state


def queryAllMovies():
    return session.query(MovieDB).all()


@app.route('/')
@app.route('/movies/')
def showMovies():
    movies = queryAllMovies()
    state = new_state()
    return render_template('demo.html', movies=movies, currentPage='application',
                           state=state, login_session=login_session)


@app.route('/movie/new/', methods=['GET', 'POST'])
def newMovie():
    if request.method == 'POST':

        if 'provider' in login_session and \
                login_session['provider'] != 'null':
            movieName = request.form['movieName']
            posterUrl = request.form['movieImage']
            movieGenre = request.form['genre']
            user_id = check_user().id

            if movieName and posterUrl and movieGenre:
                newMovie = MovieDB(
                    movieName=movieName,
                    posterUrl=posterUrl,
                    genre=movieGenre,
                    user_id=user_id,
                )
                session.add(newMovie)
                session.commit()
                return redirect(url_for('showMovie'))
            else:
                state = new_state()
                return render_template(
                    'newItem.html',
                    currentPage='new',
                    title='Add A Movie',
                    errorMsg='No Empty Fields',
                    state=state,
                    login_session=login_session,
                )
        else:
            state = new_state()
            movies = queryAllMovies()
            return render_template(
                'demo.html',
                movies=movies,
                currentPage='demo',
                state=state,
                login_session=login_session,
                errorMsg='Please Login',
            )
    elif 'provider' in login_session and login_session['provider'] \
            != 'null':
        state = new_state()
        return render_template('newItem.html', currentPage='new',
                               title='Add A Movie', state=state,
                               login_session=login_session)
    else:
        state = new_state()
        movies = queryAllMovies()
        return render_template(
            'demo.html',
            movies=movies,
            currentPage='demo',
            state=state,
            login_session=login_session,
            errorMsg='Please Login',
        )


@app.route('/movies/genre/<string:genre>/')
def sortMovies(genre):
    movies = session.query(MovieDB).filter_by(genre=genre).all()
    state = new_state()
    return render_template(
        'demo.html',
        movies=movies,
        currentPage='demo',
        error='Sorry!',
        state=state,
        login_session=login_session)


@app.route('/movies/genre/<string:genre>/<int:movieId>/')
def movieDetail(genre, movieId):
    movie = session.query(MovieDB).filter_by(id=movieId,
                                             genre=genre).first()
    state = new_state()
    if movie:
        return render_template('itemDetail.html', movie=movie,
                               currentPage='detail', state=state,
                               login_session=login_session)
    else:
        return render_template('demo.html', currentPage='demo',
                               error="""No MOVIE OF THIS TYPE""",
                               state=state,
                               login_session=login_session)


@app.route('/movies/genre/<string:genre>/<int:movieId>/edit/',
           methods=['GET', 'POST'])
def editMovieDetails(genre, movieId):
    movie = session.query(MovieDB).filter_by(id=movieId,
                                             genre=genre).first()
    if request.method == 'POST':

        if 'provider' in login_session and login_session['provider'] \
                != 'null':
            movieName = request.form['movieName']
            posterUrl = request.form['movieImage']
            movieGenre = request.form['genre']
            user_id = check_user().id
            admin_id = check_admin().id

            if movie.user_id == user_id or user_id == admin_id:
                if movieName and posterUrl and movieGenre:
                    movie.movieName = movieName
                    movie.posterUrl = posterUrl
                    movie.genre = movieGenre
                    session.add(movie)
                    session.commit()
                    return redirect(url_for('movieDetail',
                                            genre=movie.genre,
                                            movieId=movie.id))
                else:
                    state = new_state()
                    return render_template(
                        'editItem.html',
                        currentPage='edit',
                        title='Edit Movie Details',
                        movie=movie,
                        state=state,
                        login_session=login_session,
                        errorMsg='Every Field is Required!',
                    )
            else:
                state = new_state()
                return render_template(
                    'itemDetail.html',
                    movie=movie,
                    currentPage='detail',
                    state=state,
                    login_session=login_session,
                    errorMsg='You cannot edit movie Details!')
        else:
            state = new_state()
            return render_template(
                'itemDetail.html',
                movie=movie,
                currentPage='detail',
                state=state,
                login_session=login_session,
                errorMsg='Please Login!',
            )
    elif movie:
        state = new_state()
        if 'provider' in login_session and login_session['provider'] \
                != 'null':
            user_id = check_user().id
            admin_id = check_admin().id
            if user_id == movie.user_id:
                movie.description = movie.description.replace('<br>,''\n')
                return render_template(
                    'editItem.html',
                    currentPage='edit',
                    title='Edit Movie Details',
                    movie=movie,
                    state=state,
                    login_session=login_session,
                )
            else:
                return render_template(
                    'itemDetail.html',
                    movie=movie,
                    currentPage='detail',
                    state=state,
                    login_session=login_session,
                    errorMsg='You cannot edit movie Details!')
        else:
            return render_template(
                'itemDetail.html',
                movie=movie,
                currentPage='detail',
                state=state,
                login_session=login_session,
                errorMsg='Please Login',
            )
    else:
        state = new_state()
        return render_template('demo.html', currentPage='main',
                               error=""" No Movie Found
                               with this Genre(""",
                               state=state,
                               login_session=login_session)


@app.route('/movies/genre/<string:genre>/<int:movieId>/delete/')
def deleteMovie(genre, movieId):
    movie = session.query(MovieDB).filter_by(genre=genre,
                                             id=movieId).first()
    state = new_state()
    if movie:

        # check if user is logged in or not

        if 'provider' in login_session and login_session['provider'] \
                != 'null':
            user_id = check_user().id
            admin_id = check_admin().id
            if user_id == movie.user_id or user_id == admin_id:
                session.delete(movie)
                session.commit()
                return redirect(url_for('showMovies'))
            else:
                return render_template(
                    'itemDetail.html',
                    movie=movie,
                    currentPage='detail',
                    state=state,
                    login_session=login_session,
                    errorMsg='You Cannot delete the movie'
                )
        else:
            return render_template(
                'itemDetail.html',
                movie=movie,
                currentPage='detail',
                state=state,
                login_session=login_session,
                errorMsg='Please Login!',
            )
    else:
        return render_template('demo.html', currentPage='main',
                               error=""" No Movie Found
                               with this Genre(""",
                               state=state,
                               login_session=login_session)


@app.route('/gconnect', methods=['POST'])
def gconnect():

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    request.get_data()
    code = request.data.decode('utf-8')

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('credentials')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['id']
        del login_session['name']
        del login_session['email']
        del login_session['img']

        # response = make_response(json.dumps('Successfully disconnected.'), 200)
        # response.headers['Content-Type'] = 'application/json'
        response = make_response(json.dumps({'state': 'loggedOut'}), 200)
        flash("You are now logged out.")
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/movies.json/')
def moviesJSON():
    movies = session.query(MovieDB).all()
    return jsonify(Movies=[movie.serialize for movie in movies])

@app.route('/movies/genre/<string:genre>.json/')
def movieGenreSON(genre):
    movies = session.query(MovieDB).filter_by(genre=genre).all()
    return jsonify(Movies=[movie.serialize for movie in movies])


@app.route('/movies/genre/<string:genre>/<int:movieId>.json/')
def movieJSON(genre, movieId):
    movie = session.query(MovieDB).filter_by(genre=genre,
                                             id=movieId).first()
    return jsonify(Movie=movie.serialize)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
