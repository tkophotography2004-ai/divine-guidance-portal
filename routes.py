from flask import render_template, request, redirect, url_for, flash, jsonify, session, current_app
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, date, time, timedelta
import stripe
import pytz
import requests
import json
from app.models import db, User, Booking, Payment, SessionLog, AvailableSlot
from app.forms import RegistrationForm, LoginForm, BookingForm, PaymentForm, ContactForm, AdminSlotForm

# Import app configuration
from app import app, STRIPE_PUBLISHABLE_KEY, HEDRA_API_KEY, SESSION_TYPES, BUSINESS_NAME, TIKTOK_URL, TIMEZONE

@app.route('/')
def home():
    """Homepage with Zahrah branding and service overview"""
    return render_template('home.html', 
                         business_name=BUSINESS_NAME,
                         session_types=SESSION_TYPES,
                         tiktok_url=TIKTOK_URL)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with validation"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Welcome to Divine Talks! Your spiritual journey begins now.', 'success')
        login_user(user)
        return redirect(url_for('dashboard'))

    return render_template('register.html', form=form, business_name=BUSINESS_NAME)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login with username or email support"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        # Try username first, then email
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            user = User.query.filter_by(email=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)

            # Redirect to next page if available
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            # Redirect based on user role
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid username/email or password. Please try again.', 'error')

    return render_template('login.html', form=form, business_name=BUSINESS_NAME)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been safely logged out. Until we meet again! 🌟', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with booking overview"""
    # Get user's upcoming sessions
    upcoming_sessions = Booking.query.filter_by(
        user_id=current_user.id,
        payment_status='succeeded'
    ).filter(
        Booking.booking_date >= date.today()
    ).order_by(Booking.booking_date.asc(), Booking.booking_time.asc()).all()

    # Get recent booking history
    past_sessions = Booking.query.filter_by(
        user_id=current_user.id
    ).filter(
        Booking.booking_date < date.today()
    ).order_by(Booking.booking_date.desc()).limit(5).all()

    return render_template('dashboard.html',
                         upcoming_sessions=upcoming_sessions,
                         past_sessions=past_sessions,
                         business_name=BUSINESS_NAME,
                         session_types=SESSION_TYPES)

@app.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    """Session booking with CST timezone handling"""
    form = BookingForm()

    if form.validate_on_submit():
        # Get session type details
        session_type_key = form.session_type.data
        session_details = SESSION_TYPES[session_type_key]

        # Parse booking time
        booking_time_str = form.booking_time.data
        booking_time = datetime.strptime(booking_time_str, '%H:%M').time()

        # Create booking
        booking = Booking(
            user_id=current_user.id,
            session_type=session_type_key,
            booking_date=form.booking_date.data,
            booking_time=booking_time,
            duration=session_details['duration'],
            price=session_details['price'],
            special_requests=form.special_requests.data
        )

        db.session.add(booking)
        db.session.commit()

        # Redirect to payment
        return redirect(url_for('payment', booking_id=booking.id))

    return render_template('book.html', 
                         form=form, 
                         session_types=SESSION_TYPES,
                         business_name=BUSINESS_NAME)

@app.route('/get_available_times')
@login_required
def get_available_times():
    """AJAX endpoint for getting available times for a date"""
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'Date required'}), 400

    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        available_times = BookingForm.get_available_times_for_date(selected_date)
        return jsonify({'times': available_times})
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

@app.route('/payment/<int:booking_id>')
@login_required
def payment(booking_id):
    """Payment page with Stripe integration"""
    booking = Booking.query.get_or_404(booking_id)

    # Ensure user owns this booking
    if booking.user_id != current_user.id:
        flash('You can only pay for your own bookings.', 'error')
        return redirect(url_for('dashboard'))

    # Check if already paid
    if booking.payment_status == 'succeeded':
        flash('This session has already been paid for.', 'info')
        return redirect(url_for('dashboard'))

    try:
        # Create Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=booking.price,
            currency='usd',
            metadata={
                'booking_id': booking.id,
                'user_id': current_user.id,
                'session_type': booking.session_type
            }
        )

        # Update booking with payment intent
        booking.stripe_payment_intent_id = intent.id
        db.session.commit()

        return render_template('payment.html',
                             booking=booking,
                             client_secret=intent.client_secret,
                             stripe_publishable_key=STRIPE_PUBLISHABLE_KEY,
                             business_name=BUSINESS_NAME)

    except stripe.error.StripeError as e:
        flash(f'Payment setup error: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/payment_success/<int:booking_id>')
@login_required
def payment_success(booking_id):
    """Payment success confirmation"""
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    # Mark booking as paid
    booking.payment_status = 'succeeded'
    booking.paid_at = datetime.utcnow()
    booking.status = 'paid'

    # Create payment record
    payment = Payment(
        booking_id=booking.id,
        stripe_payment_intent_id=booking.stripe_payment_intent_id,
        amount=booking.price,
        status='succeeded'
    )

    db.session.add(payment)
    db.session.commit()

    flash('Payment successful! Your session with Zahrah is confirmed. 🌟', 'success')
    return render_template('payment_success.html', 
                         booking=booking,
                         business_name=BUSINESS_NAME)

@app.route('/session_room/<int:booking_id>')
@login_required
def session_room(booking_id):
    """Session room for Hedra avatar interaction"""
    booking = Booking.query.get_or_404(booking_id)

    # Security checks
    if booking.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    if booking.payment_status != 'succeeded':
        flash('Please complete payment before accessing your session.', 'error')
        return redirect(url_for('payment', booking_id=booking.id))

    # Check if session is today and within time window
    now_cst = datetime.now(TIMEZONE)
    session_datetime_cst = booking.booking_datetime_cst

    # Allow access 15 minutes before session time
    access_time = session_datetime_cst - timedelta(minutes=15)
    end_time = session_datetime_cst + timedelta(minutes=booking.duration + 15)

    if now_cst < access_time:
        flash(f'Session room opens at {access_time.strftime("%I:%M %p CST")}', 'info')
        return redirect(url_for('dashboard'))

    if now_cst > end_time:
        flash('Session time has ended.', 'info')
        return redirect(url_for('dashboard'))

    return render_template('session_room.html',
                         booking=booking,
                         hedra_api_key=HEDRA_API_KEY,
                         business_name=BUSINESS_NAME)

@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard for Tina"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))

    # Get statistics
    today = date.today()

    # Recent bookings
    recent_bookings = Booking.query.order_by(
        Booking.created_at.desc()
    ).limit(10).all()

    # Revenue statistics
    total_revenue = db.session.query(db.func.sum(Booking.price)).filter(
        Booking.payment_status == 'succeeded'
    ).scalar() or 0

    monthly_revenue = db.session.query(db.func.sum(Booking.price)).filter(
        Booking.payment_status == 'succeeded',
        Booking.created_at >= today.replace(day=1)
    ).scalar() or 0

    total_bookings = Booking.query.count()
    paid_bookings = Booking.query.filter_by(payment_status='succeeded').count()

    conversion_rate = (paid_bookings / total_bookings * 100) if total_bookings > 0 else 0

    return render_template('admin/dashboard.html',
                         recent_bookings=recent_bookings,
                         total_revenue=total_revenue / 100,  # Convert to dollars
                         monthly_revenue=monthly_revenue / 100,
                         total_bookings=total_bookings,
                         conversion_rate=round(conversion_rate, 1),
                         business_name=BUSINESS_NAME)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html', business_name=BUSINESS_NAME), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html', business_name=BUSINESS_NAME), 500

# Webhook handler for Stripe
@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        # Verify webhook signature (you'll need to set STRIPE_WEBHOOK_SECRET)
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET', '')
        )
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400

    # Handle payment_intent.succeeded event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        booking_id = payment_intent['metadata'].get('booking_id')

        if booking_id:
            booking = Booking.query.get(booking_id)
            if booking:
                booking.payment_status = 'succeeded'
                booking.paid_at = datetime.utcnow()
                booking.status = 'paid'
                db.session.commit()

    return 'Success', 200
