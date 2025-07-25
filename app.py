from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
import csv
from datetime import datetime
import mysql.connector

from config import MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD
from config import Config, DB_CONFIG
from models import *

app = Flask(__name__)
app.config.from_object(Config)
app.config.update(
    MAIL_SERVER=MAIL_SERVER,
    MAIL_PORT=MAIL_PORT,
    MAIL_USE_TLS=MAIL_USE_TLS,
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    UPLOAD_FOLDER='static/uploads'
)

mail = Mail(app)
db = SQLAlchemy(app)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def send_email(to, subject, body):
    msg = Message(subject, sender=MAIL_USERNAME, recipients=[to])
    msg.body = body
    mail.send(msg)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        location = request.form['location']
        hashed_password = generate_password_hash(password)

        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password, location) VALUES (%s, %s, %s, %s)",
                       (name, email, hashed_password, location))
        db_conn.commit()
        db_conn.close()

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            session['role'] = user.get('role', 'user')
            session['email'] = user['email']
            return redirect('/submit_complaint')
        else:
            flash("Invalid email or password")
            return redirect('/login')
    return render_template('login.html')

@app.route('/submit_complaint', methods=['GET', 'POST'])
def submit_complaint():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name')
        state = request.form.get('state')
        district = request.form.get('district')
        taluk = request.form.get('taluk')
        village = request.form.get('village')
        pincode = request.form.get('pincode')
        issue_type = request.form.get('issue')
        description = request.form.get('message')
        photo = request.files.get('photo')

        filename = None
        if photo and photo.filename != '':
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO complaints (user_id, name, state, district, taluk, village, pincode, issue_type, description, photo, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            session['user_id'], name, state, district, taluk, village, pincode,
            issue_type, description, filename, datetime.now()
        ))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Complaint submitted successfully.")
        return redirect(url_for('submit_complaint'))

    return render_template('submit_complaint.html')

@app.route('/track_complaints')
def track_complaints():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db_conn = get_db_connection()
    cursor = db_conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM complaints WHERE user_id = %s ORDER BY created_at DESC", (session['user_id'],))
    complaints = cursor.fetchall()
    db_conn.close()

    return render_template('track_complaints.html', complaints=complaints)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db_conn = get_db_connection()
        cursor = db_conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
        admin = cursor.fetchone()
        db_conn.close()

        if admin and check_password_hash(admin['password'], password):
            session['admin_id'] = admin['admin_id']
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid login.')

    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    db_conn = get_db_connection()
    cursor = db_conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.complaint_id, u.name AS user_name, d.department_name AS dept_name, c.issue_type, c.status, c.created_at
        FROM complaints c
        JOIN users u ON c.user_id = u.user_id
        JOIN departments d ON c.department_id = d.department_id
    """)
    complaints = cursor.fetchall()
    db_conn.close()

    return render_template('admin_dashboard.html', complaints=complaints)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

@app.route('/admin/users')
def admin_users():
    if 'admin_id' not in session:
        return redirect('/admin/login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, name, email FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin_users.html', users=users)

@app.route('/admin/update_status/<int:complaint_id>', methods=['POST'])
def update_status(complaint_id):
    if 'admin_id' not in session:
        return redirect('/admin/login')

    new_status = request.form.get('status')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT email FROM users u JOIN complaints c ON u.user_id = c.user_id WHERE c.complaint_id = %s", (complaint_id,))
    result = cursor.fetchone()
    if result:
        user_email = result[0]
        cursor.execute("UPDATE complaints SET status = %s WHERE complaint_id = %s", (new_status, complaint_id))
        conn.commit()

        subject = "Complaint Status Updated"
        body = f"Dear user,\n\nYour complaint ID {complaint_id} status has been updated to '{new_status}'.\n\nThank you."
        send_email(user_email, subject, body)

    cursor.close()
    conn.close()

    flash("Complaint status updated.")
    return redirect('/admin/dashboard')

@app.route('/my-complaints')
def my_complaints():
    if 'user_id' not in session:
        flash("Please log in to view your complaints.")
        return redirect('/login')

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM complaints WHERE user_id = %s", (user_id,))
    complaints = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('my_complaints.html', complaints=complaints)

location_data = {}

def load_location_data():
    global location_data
    with open('location_data.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            pincode = row['pincode'].strip()
            location_data[pincode] = {
                'state': row['state'].strip(),
                'district': row['district'].strip(),
                'taluk': row['taluk'].strip(),
                'village': row['village'].strip()
            }

load_location_data()

@app.route('/get_location_info', methods=['GET'])
def get_location_info():
    pincode = request.args.get('pincode', '').strip()
    if pincode in location_data:
        return jsonify(location_data[pincode])
    else:
        return jsonify({'error': 'Pincode not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
