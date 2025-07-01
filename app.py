from flask import Flask, render_template, request, redirect, session , flash
import boto3

app = Flask(__name__)

dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
MovieBookings=dynamodb.Table('MovieBookings')
SNS = boto3.client('sns', region_name='your-region')
SNS_topic_arn='arn:aws:sns:us-east-1:545009839820:Movie_booking'
# List of Movies with Details
movies = [
    {
        'title': 'Inception',
        'image': 'inception.jpg',
        'show_time': '5:00 PM',
        'price': 200,
        'rating': 4.9
    },
    {
        'title': 'Pushpa',
        'image': 'pushpa.jpg',
        'show_time': '11:00 AM',
        'price': 140,
        'rating': 4.5
    },
    {
        'title': 'Animal',
        'image': 'animal.jpg',
        'show_time': '8:00 PM',
        'price': 190,
        'rating': 4.4
    },
    {
        'title': 'Orange',
        'image': 'orange.jpg',
        'show_time': '2:00 PM',
        'price': 150,
        'rating': 4.3
    },
    {
        'title': 'RRR',
        'image': 'rrr.jpg',
        'show_time': '6:30 PM',
        'price': 220,
        'rating': 4.8
    },
    {
        'title': 'Remo',
        'image': 'remo.jpg',
        'show_time': '4:00 PM',
        'price': 160,
        'rating': 4.1
    },
]

# Home route redirects to /movies
@app.route('/')
def home():
    return redirect(url_for('show_movies'))
    return render_template('home.html')

# Shows the movie listing
@app.route('/movies')
def show_movies():
    return render_template('movies.html', movies=movies)

# Booking page for a selected movie
@app.route('/book/<title>')
def book_movie(title):
    for movie in movies:
        if movie['title'] == title:
            return render_template('book.html', movie=movie)
    return "Movie not found"

# Confirmation route (optional)
@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    name = request.form['name']
    seats = request.form['seats']
    movie_title = request.form['movie_title']
    return render_template('confirmation.html', name=name, seats=seats, movie_title=movie_title)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
