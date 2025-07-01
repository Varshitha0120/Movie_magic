from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

users = [{'id': 1, 'name': 'test', 'email': 'test@gmail.com', 'password': generate_password_hash('1234')}]
bookings = []
booking_counter = 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = next((u for u in users if u['email'] == email), None)
        if user and check_password_hash(user['password'], password):
            session['user'] = {'id': user['id'], 'name': user['name'], 'email': user['email']}
            return redirect(url_for('home1'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        user = {
            'id': len(users) + 1,
            'name': name,
            'email': email,
            'password': password
        }
        users.append(user)
        flash('Registered successfully! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/home1')
def home1():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('home1.html')
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/b1')
def b1():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('b1.html')
@app.route('/contact_us', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        print("📩 New Contact Message:")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Message: {message}")
        
        flash('Message sent successfully!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact_us.html')

@app.route('/tickets', methods=['POST'])
def tickets():
    global booking_counter
    user = session.get('user')
    if not user:
        flash('Login required')
        return redirect(url_for('login'))
    
    booking = {
        'booking_id': booking_counter,
        'user_id': user['id'],
        'movie': request.form['movie'],
        'theater': request.form['theater'],
        'address': request.form['address'],
        'price': request.form['price'],
        'seats': request.form['seats'],
        'booking_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    bookings.append(booking)
    booking_counter += 1
    return render_template('tickets.html', booking=booking)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)