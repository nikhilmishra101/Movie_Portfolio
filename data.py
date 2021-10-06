from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

#Create DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.INTEGER,primary_key=True)
    title = db.Column(db.String(250),unique=True,nullable=False)
    year = db.Column(db.INTEGER,nullable=False)
    description = db.Column(db.Text(4294000000),nullable=False)
    rating = db.Column(db.FLOAT,nullable=True)
    ranking = db.Column(db.INTEGER,nullable=True)
    review = db.Column(db.Text(4294000000),nullable=True)
    img_url = db.Column(db.String,nullable=False)


db.create_all()

#Api request
API_URL = "https://api.themoviedb.org/3"
API_KEY = os.environ.get("API_KEY")
MOVIE_DB_IMG_URL = "https://image.tmdb.org/t/p/w500"



#CREATE Ratings edit FORM
class MovieRatingsForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField('Done')

#CREATE Movie add form
class MovieAdd(FlaskForm):
    movie_title = StringField("Movie Title",validators=[DataRequired()])
    submit = SubmitField("Add Movie")


def get_movies_by_name(movie_name):
        params = {
            "api_key": API_KEY,
            "query": movie_name,
        }
        return requests.get(f"{API_URL}/search/movie", params=params).json()["results"]

def get_movie_by_id(movie_id):
    params = {
        "api_key":API_KEY,
    }
    return requests.get(f"{API_URL}/movie/{movie_id}",params=params).json()


@app.route("/",methods=["GET"])
def home():
    #Create a list of all movies sorted by their ratings in desc order
    all_movies = Movie.query.order_by(Movie.rating).all()

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies)-i

    db.session.commit()
    return render_template("index.html",movies=all_movies)

@app.route("/edit",methods=["GET","POST"])
def edit():
    form = MovieRatingsForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html",movie=movie,form=form)

@app.route("/add",methods=["GET","POST"])
def add():
    form = MovieAdd()
    if form.validate_on_submit():
        movie_name = form.movie_title.data
        all_movies = get_movies_by_name(movie_name)
        return render_template('select.html',movies=all_movies)
    return render_template('add.html',form=form)

@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/find")
def find_movie():
    movie_id = request.args.get("id")
    movie_details = get_movie_by_id(movie_id)
    #Adding new movie to database/populating the database
    new_movie = Movie(
        title = movie_details["title"],
        year = movie_details["release_date"].split("-")[0],
        img_url = f"{MOVIE_DB_IMG_URL}{movie_details['poster_path']}",
        description = movie_details["overview"]

    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for("edit",id=new_movie.id))
if __name__ == '__main__':
    app.run()
