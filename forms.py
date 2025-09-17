from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, TimeField, PasswordField, SubmitField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from datetime import datetime, date, time
import pytz
from app.models import User

class RegistrationForm(FlaskForm):
    """User registration form"""
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=50)])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number (Optional)', validators=[Optional(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Create My Account')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email or login.')

class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class BookingForm(FlaskForm):
    """Session booking form with CST timezone handling"""
    session_type = SelectField('Session Type', 
        choices=[
            ('quick_guidance', 'Quick Guidance - $17 (10 minutes)'),
            ('deep_dive', 'Deep Dive Session - $97 (30 minutes)'),
            ('intensive_healing', 'Intensive Healing - $297 (60 minutes)')
        ],
        validators=[DataRequired()]
    )
    booking_date = DateField('Preferred Date', validators=[DataRequired()])
    booking_time = SelectField('Preferred Time (CST)', validators=[DataRequired()])
    special_requests = TextAreaField('Special Focus Areas or Questions', 
        validators=[Optional(), Length(max=500)],
        render_kw={"placeholder": "Share what you'd like Zahrah to focus on during your session..."}
    )
    submit = SubmitField('Book This Session')

    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        self.populate_time_slots()

    def populate_time_slots(self):
        """Generate available time slots based on Tina's CST schedule"""
        # This will be populated dynamically based on selected date
        self.booking_time.choices = [('', 'Select a time...')]

    def validate_booking_date(self, booking_date):
        if booking_date.data < date.today():
            raise ValidationError('Please select a future date.')

    @staticmethod
    def get_available_times_for_date(selected_date):
        """Get available time slots for a specific date in CST"""
        from datetime import time, timedelta

        day_of_week = selected_date.weekday()  # 0=Monday, 6=Sunday
        available_times = []

        if day_of_week < 5:  # Monday to Friday
            # 5:30 PM to 10:00 PM CST
            start_hour, start_min = 17, 30
            end_hour = 22
        else:  # Saturday and Sunday
            # 8:00 AM to 10:00 PM CST  
            start_hour, start_min = 8, 0
            end_hour = 22

        # Generate 30-minute slots
        current_time = time(start_hour, start_min)
        end_time = time(end_hour, 0)

        while current_time < end_time:
            time_str = current_time.strftime("%I:%M %p")
            available_times.append((current_time.strftime("%H:%M"), f"{time_str} CST"))

            # Add 30 minutes
            minutes = current_time.minute + 30
            hours = current_time.hour
            if minutes >= 60:
                minutes -= 60
                hours += 1
            current_time = time(hours, minutes)

        return available_times

class PaymentForm(FlaskForm):
    """Payment processing form for Stripe integration"""
    booking_id = HiddenField('Booking ID', validators=[DataRequired()])
    stripe_token = HiddenField('Stripe Token')
    submit = SubmitField('Complete Payment')

class ContactForm(FlaskForm):
    """Contact/inquiry form"""
    name = StringField('Your Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=5, max=100)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('Send Message')

class AdminSlotForm(FlaskForm):
    """Admin form for managing available time slots"""
    day_of_week = SelectField('Day of Week', 
        choices=[
            (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), 
            (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
        ],
        validators=[DataRequired()], coerce=int
    )
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Time Slot')

    def validate_end_time(self, end_time):
        if self.start_time.data and end_time.data:
            if end_time.data <= self.start_time.data:
                raise ValidationError('End time must be after start time.')
