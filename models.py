# models.py
from app import db

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    location = db.Column(db.String(255))
    registered_at = db.Column(db.DateTime)

from app import db
from datetime import datetime

class Complaint(db.Model):
    __tablename__ = 'complaints'
    complaint_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    photo_url = db.Column(db.String(255))
    location = db.Column(db.String(255))
    status = db.Column(db.Enum('Pending', 'In Progress', 'Resolved', 'Escalated'), default='Pending')
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='complaints')
    department = db.relationship('Department', backref='complaints')

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Department(db.Model):
    __tablename__ = 'departments'

    department_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    complaint_types_handled = db.Column(db.Text)  # Comma-separated list

    def __repr__(self):
        return f'<Department {self.name}>'



class Admin(db.Model):
    __tablename__ = 'admins'
    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ComplaintChat(db.Model):
    __tablename__ = 'complaint_chat'
    chat_id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.complaint_id'), nullable=False)
    sender_role = db.Column(db.Enum('user', 'admin', 'department'), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    complaint = db.relationship('Complaint', backref='chat_messages')


class Notification(db.Model):
    __tablename__ = 'notifications'
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.complaint_id'), nullable=True)
    type = db.Column(db.Enum('email', 'sms'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('sent', 'failed'), default='sent')
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')
    complaint = db.relationship('Complaint', backref='notifications', foreign_keys=[complaint_id])


class Escalation(db.Model):
    __tablename__ = 'escalations'
    escalation_id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.complaint_id'), nullable=False)
    escalated_at = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.Text)

    complaint = db.relationship('Complaint', backref='escalation')
