from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'movie-magic-local'

# ------------------ In-Memory Storage ------------------
users = []
bookings = []

# ------------------ Movie List ------------------
# UPDATED: Added direct image URLs to each movie dictionary
movies = [
    {"id": 1, "name": "Animal", "time": "6:00 PM", "price": 150, "rating": 4.8, "image": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/animal.jpg-F4j0Ros35NLeZIc579D1MkyKEa9nOn.jpeg"},
    {"id": 2, "name": "Devara", "time": "3:30 PM", "price": 180, "rating": 4.7, "image": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/devara.jpg-Mtw6HskL11G2Kdd9O0KZJ4IMMAAq5G.jpeg"},
    {"id": 3, "name": "Fidaa", "time": "1:00 PM", "price": 160, "rating": 4.6, "image": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/fidaa.jpg-4ZBKfGQPMEDv88sleQlXehLnADe2OA.jpeg"},
    {"id": 4, "name": "Inception", "time": "5:00 PM", "price": 200, "rating": 4.9, "image": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/inception.jpg-jeoFITtgHCkARSYtqzS56A0AVD2ulh.jpeg"},
    {"id": 5, "name": "Orange", "time": "11:00 AM", "price": 140, "rating": 4.5, "image": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/orange.jpg-GXC0CLM5byxt0yMGz1m1qoponmHsHa.jpeg"},
    {"id": 6, "name": "Pushpa", "time": "8:00 PM", "price": 190, "rating": 4.4, "image": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/pushpa.jpg-jFXViTQhSrNObtbvMjgkjzbTGtONOb.jpeg"},
    {"id": 7, "name": "Remo", "time": "2:30 PM", "price": 170, "rating": 4.6, "image": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/remo.jpg-vDzS2cPf2UK89LAPJZDxNruD0hPm76.jpeg"},
    {"id": 8, "name": "Sakhi", "time": "10:00 AM", "price": 160, "rating": 4.3, "image": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/sakhi.jpg-tRCIG6nu4lNZCs4sSZD3MXRyVfcVKv.jpeg"},
]

@app.route('/')
def index():
    return redirect(url_for('login'))

# ---------------- Login ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = request.form.get('remember')
        user = next((u for u in users if u['email'] == email and u['password'] == password), None)
        if user:
            session['user'] = email
            if remember:
                session.permanent = True
            return redirect(url_for('home'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

# ---------------- Register ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        if any(u['email'] == email for u in users):
            return render_template('register.html', error="User already exists")
        users.append({
            'email': email,
            'password': password,
            'phone': phone
        })
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ---------------- Home ----------------
@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('home1.html')

# ---------------- Movies ----------------
@app.route('/movies')
def movies_page():
    if 'user' not in session:
        return redirect(url_for('login'))
    query = request.args.get('q', '')
    filtered = [m for m in movies if query.lower() in m['name'].lower()]
    return render_template('movies.html', movies=filtered)

# ---------------- Booking ----------------
@app.route('/book/<int:id>', methods=['GET', 'POST'])
def book_ticket(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    movie = next((m for m in movies if m['id'] == id), None)
    if not movie:
        return "Movie not found", 404
    if request.method == 'POST':
        name = request.form['name']
        try:
            tickets = int(request.form['tickets'])
            email = session['user']
            booking_id = str(random.randint(100000, 999999))
            bookings.append({
                'booking_id': booking_id,
                'email': email,
                'username': name,
                'movie': movie['name'],
                'count': tickets
            })
            print(f"[EMAIL SIMULATION] Sent booking confirmation to {email}")
            print(f"Hi {name}, You booked {tickets} ticket(s) for {movie['name']}. Enjoy your movie!")
            return render_template("success.html", movie=movie, name=name, tickets=tickets)
        except ValueError:
            return render_template("book.html", movie=movie, error="Invalid ticket count")
    return render_template("book.html", movie=movie)

# ---------------- Admin ----------------
@app.route('/admin')
def admin():
    return render_template('admin.html', bookings=bookings)

# ---------------- Forgot Password ----------------
@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        user = next((u for u in users if u['email'] == email), None)
        if user:
            code = random.randint(1000, 9999)
            session['reset_code'] = code
            session['reset_email'] = email
            print(f"[EMAIL SIMULATION] Sent reset code to {email}: {code}")
            return redirect(url_for('verify_code'))
        return render_template("forgot_password.html", error="Email not registered")
    return render_template("forgot_password.html")

@app.route('/verify-code', methods=['GET', 'POST'])
def verify_code():
    if request.method == 'POST':
        entered = request.form['code']
        if 'reset_code' in session and entered == str(session['reset_code']):
            return redirect(url_for('reset_password'))
        return render_template('verify_code.html', error="Invalid code.")
    return render_template('verify_code.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_pass = request.form['password']
        email = session.get('reset_email')
        user = next((u for u in users if u['email'] == email), None)
        if user:
            user['password'] = new_pass
        session.pop('reset_code', None)
        session.pop('reset_email', None)
        return redirect(url_for('login'))
    return render_template('reset_password.html')

# ---------------- Run ----------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
