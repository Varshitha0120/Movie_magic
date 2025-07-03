from flask import Flask, render_template, request, redirect, url_for, session
import boto3
import random
import os

app = Flask(__name__)
app.secret_key = '9a4f90b2b6df594f2e16f6c1f3d9e0ab0cd431c0f0176a2544e740c94cb75a0e'

# AWS DynamoDB Setup
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
users_table = dynamodb.Table('users')
bookings_table = dynamodb.Table('bookings')

# AWS SNS Setup
sns = boto3.client('sns', region_name='us-east-1')

# Movies data
movies = [
    {"id": 1, "name": "Animal", "time": "6:00 PM", "price": 150, "rating": 4.8, "image": "animal.jpg"},
    {"id": 2, "name": "Devara", "time": "3:30 PM", "price": 180, "rating": 4.7, "image": "devara.jpg"},
    {"id": 3, "name": "Fidaa", "time": "1:00 PM", "price": 160, "rating": 4.6, "image": "fidaa.jpg"},
    {"id": 4, "name": "Inception", "time": "5:00 PM", "price": 200, "rating": 4.9, "image": "inception.jpg"},
    {"id": 5, "name": "Orange", "time": "11:00 AM", "price": 140, "rating": 4.5, "image": "orange.jpg"},
    {"id": 6, "name": "Pushpa", "time": "8:00 PM", "price": 190, "rating": 4.4, "image": "pushpa.jpg"},
    {"id": 7, "name": "Remo", "time": "2:30 PM", "price": 170, "rating": 4.6, "image": "remo.jpg"},
    {"id": 8, "name": "Sakhi", "time": "10:00 AM", "price": 160, "rating": 4.3, "image": "sakhi.jpg"},
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

        res = users_table.get_item(Key={'email': email})
        user = res.get('Item')

        if user and user['password'] == password:
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

        existing = users_table.get_item(Key={'email': email})
        if 'Item' in existing:
            return render_template('register.html', error="User already exists")

        users_table.put_item(Item={
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

            bookings_table.put_item(Item={
                'booking_id': booking_id,
                'email': email,
                'username': name,
                'movie': movie['name'],
                'count': tickets
            })

            # Send booking email via SNS
            sns.publish(
                TopicArn='arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:YOUR_TOPIC_NAME',  # OR use Email endpoint
                Subject="🎟 Movie Booking Confirmation",
                Message=f"Hi {name},\n\nYou booked {tickets} ticket(s) for {movie['name']}.\nEnjoy your movie!\n\nMovie Magic 🍿"
            )

            return render_template("success.html", movie=movie, name=name, tickets=tickets)
        except ValueError:
            return render_template("book.html", movie=movie, error="Invalid ticket count")
    return render_template("book.html", movie=movie)

# ---------------- Admin ----------------
@app.route('/admin')
def admin():
    all_bookings = bookings_table.scan().get('Items', [])
    return render_template('admin.html', bookings=all_bookings)

# ---------------- Forgot Password ----------------
@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        user = users_table.get_item(Key={'email': email}).get('Item')
        if user:
            code = random.randint(1000, 9999)
            session['reset_code'] = code
            session['reset_email'] = email

            # Send code via SNS email
            sns.publish(
                TopicArn='arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:YOUR_TOPIC_NAME',
                Subject="🔐 Password Reset Code",
                Message=f"Your password reset code is: {code}"
            )

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
        users_table.update_item(
            Key={'email': email},
            UpdateExpression="SET password = :p",
            ExpressionAttributeValues={':p': new_pass}
        )
        session.pop('reset_code', None)
        session.pop('reset_email', None)
        return redirect(url_for('login'))
    return render_template('reset_password.html')

# ---------------- Run ----------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)