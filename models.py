from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import pytz

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and profile management"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Booking(db.Model):
    """Booking model for session management"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_type = db.Column(db.String(50), nullable=False)  # quick_guidance, deep_dive, intensive_healing
    booking_date = db.Column(db.Date, nullable=False)
    booking_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    price = db.Column(db.Integer, nullable=False)  # in cents
    status = db.Column(db.String(20), default='pending')  # pending, paid, completed, cancelled
    special_requests = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Payment tracking
    stripe_payment_intent_id = db.Column(db.String(255), nullable=True)
    payment_status = db.Column(db.String(20), default='pending')  # pending, succeeded, failed
    paid_at = db.Column(db.DateTime, nullable=True)

    @property
    def booking_datetime_cst(self):
        """Returns booking datetime in CST"""
        utc_dt = datetime.combine(self.booking_date, self.booking_time)
        cst = pytz.timezone('US/Central')
        return cst.localize(utc_dt)

    @property
    def price_dollars(self):
        """Returns price in dollars"""
        return self.price / 100

    @property
    def session_type_display(self):
        """Returns formatted session type name"""
        type_names = {
            'quick_guidance': 'Quick Guidance',
            'deep_dive': 'Deep Dive Session', 
            'intensive_healing': 'Intensive Healing'
        }
        return type_names.get(self.session_type, self.session_type)

class AvailableSlot(db.Model):
    """Available time slots for CST timezone"""
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    @staticmethod
    def get_tina_schedule():
        """Returns Tina's availability schedule in CST"""
        # Weekdays: 5:30 PM - 10:00 PM CST
        # Weekends: 8:00 AM - 10:00 PM CST
        from datetime import time

        slots = []

        # Monday through Friday (0-4)
        for day in range(5):  # 0=Monday to 4=Friday
            slots.append({
                'day_of_week': day,
                'start_time': time(17, 30),  # 5:30 PM
                'end_time': time(22, 0)      # 10:00 PM
            })

        # Saturday and Sunday (5-6)
        for day in [5, 6]:  # 5=Saturday, 6=Sunday
            slots.append({
                'day_of_week': day,
                'start_time': time(8, 0),    # 8:00 AM
                'end_time': time(22, 0)      # 10:00 PM
            })

        return slots

class Payment(db.Model):
    """Payment tracking for Stripe integration"""
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    stripe_payment_intent_id = db.Column(db.String(255), unique=True, nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # in cents
    currency = db.Column(db.String(3), default='usd')
    status = db.Column(db.String(20), nullable=False)  # succeeded, failed, canceled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    booking = db.relationship('Booking', backref='payments')

class SessionLog(db.Model):
    """Log of actual sessions conducted"""
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    session_started_at = db.Column(db.DateTime, nullable=True)
    session_ended_at = db.Column(db.DateTime, nullable=True)
    actual_duration = db.Column(db.Integer, nullable=True)  # in minutes
    session_notes = db.Column(db.Text, nullable=True)
    user_rating = db.Column(db.Integer, nullable=True)  # 1-5 stars
    user_feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    booking = db.relationship('Booking', backref='session_logs')
