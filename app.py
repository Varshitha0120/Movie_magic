from flask import Flask, render_template, request, redirect, session, flash, url_for
import boto3
app = Flask(__name__)
app.secret_key = '9a4f90b2b6df594f2e16f6c1f3d9e0ab0cd431c0f0176a2544e740c94cb75a0e'
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        password = request.form.get('setPwd')
        confirm_password = request.form.get('confirmPwd')

        if not all([fname, lname, email, password, confirm_password]):
            return "All fields are required.", 400

        if password != confirm_password:
            return "Passwords do not match.", 400

        # Check if user already exists
        try:
            existing = users_table.get_item(Key={"email": email}).get("Item")
            if existing:
                return "User already registered.", 400
        except Exception as e:
            print("Error checking user:", e)
            return "Database error", 500

        # Insert user
        try:
            users_table.put_item(Item={
                "first_name": fname,
                "last_name": lname,
                "email": email,
                "password": password
            })
            return redirect(url_for('index'))
        except Exception as e:
            print("Error inserting user:", e)
            return "Registration failed", 500

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            user = users_table.get_item(Key={"email": email}).get("Item")
            if user and user['password'] == password:
                session['user'] = email
                return redirect(url_for('main'))
        except Exception as e:
            print("Login error:", e)

        flash("Invalid credentials")
        return redirect(url_for('login'))

    return render_template('login.html')

# AWS Services Configuration
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
MovieBookings = dynamodb.Table('MovieBookings')

SNS = boto3.client('sns', region_name='us-east-1')
SNS_topic_arn = 'arn:aws:sns:us-east-1:545009839820:Movie_booking'

# Movie List
movies = [
    {'title': 'Inception', 'image': 'inception.jpg', 'show_time': '5:00 PM', 'price': 200, 'rating': 4.9},
    {'title': 'Pushpa', 'image': 'pushpa.jpg', 'show_time': '11:00 AM', 'price': 140, 'rating': 4.5},
    {'title': 'Animal', 'image': 'animal.jpg', 'show_time': '8:00 PM', 'price': 190, 'rating': 4.4},
    {'title': 'Orange', 'image': 'orange.jpg', 'show_time': '2:00 PM', 'price': 150, 'rating': 4.3},
    {'title': 'RRR', 'image': 'rrr.jpg', 'show_time': '6:30 PM', 'price': 220, 'rating': 4.8},
    {'title': 'Remo', 'image': 'remo.jpg', 'show_time': '4:00 PM', 'price': 160, 'rating': 4.1},
]

# Home route → redirect to movies
@app.route('/')
def home():
    return redirect(url_for('show_movies'))

# Movies Page
@app.route('/movies')
def show_movies():
    return render_template('movies.html', movies=movies)

# Book a Movie
@app.route('/book/<title>')
def book_movie(title):
    for movie in movies:
        if movie['title'] == title:
            return render_template('book.html', movie=movie)
    return "Movie not found"

# Confirm Booking → Save to DynamoDB + Send SNS
@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    name = request.form['name']
    seats = request.form['seats']
    movie_title = request.form['movie_title']
    email = request.form.get('email')  # Optional: get email for SNS

    # Save to DynamoDB
    MovieBookings.put_item(Item={
        'name': name,
        'movie_title': movie_title,
        'seats': seats
    })

    # Send SNS notification
    message = f"{name} booked {seats} seat(s) for {movie_title}"
    try:
        SNS.publish(
            TopicArn=SNS_topic_arn,
            Message=message,
            Subject='🎬 Movie Booking Confirmed'
        )
    except Exception as e:
        print("SNS Error:", e)

    return render_template('confirmation.html', name=name, seats=seats, movie_title=movie_title)

# Run App
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
