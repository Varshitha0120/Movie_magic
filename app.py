from flask import Flask, render_template, request, redirect, session, flash, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for sessions

# Movie List
movies = [
    {
        'title': 'Inception',
        'image': 'images/inception.jpg',
        'show_time': '5:00 PM',
        'price': 200,
        'rating': 4.9
    },
    {
        'title': 'Pushpa',
        'image': 'images/pushpa.jpg',
        'show_time': '11:00 AM',
        'price': 140,
        'rating': 4.5
    },
    {
        'title': 'Animal',
        'image': 'images/animal.jpg',
        'show_time': '8:00 PM',
        'price': 190,
        'rating': 4.4
    },
    {
        'title': 'Orange',
        'image': 'images/orange.jpg',
        'show_time': '2:00 PM',
        'price': 150,
        'rating': 4.3
    },
    {
        'title': 'RRR',
        'image': 'images/rrr.jpg',
        'show_time': '6:30 PM',
        'price': 220,
        'rating': 4.8
    },
    {
        'title': 'Remo',
        'image': 'images/remo.jpg',
        'show_time': '4:00 PM',
        'price': 160,
        'rating': 4.1
    }
]

# Dummy user store for local use
users = {}

# Home page
@app.route('/')
def home():
    return render_template('home.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users:
            flash('Email already registered!')
        else:
            users[email] = password
            flash('Registered successfully!')
            return redirect(url_for('login'))
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if users.get(email) == password:
            session['user'] = email
            return redirect(url_for('show_movies'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

# Show Movies
@app.route('/movies')
def show_movies():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('movies.html', movies=movies)

# Book Movie
@app.route('/book/<title>', methods=['GET', 'POST'])
def book_movie(title):
    if 'user' not in session:
        return redirect(url_for('login'))

    movie = next((m for m in movies if m['title'] == title), None)
    if not movie:
        return "Movie not found", 404

    if request.method == 'POST':
        name = request.form['name']
        seats = int(request.form['seats'])
        total_price = seats * movie['price']
        return render_template('confirmation.html', name=name, seats=seats, movie=movie, total_price=total_price)

    return render_template('book.html', movie=movie)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('login'))

# Run app
if __name__ == '__main__':
    app.run(debug=True, port=5000)