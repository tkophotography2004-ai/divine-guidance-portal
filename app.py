import os
import secrets
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import stripe
import pytz
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_urlsafe(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///divine_talks.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')

# Hedra configuration  
HEDRA_API_KEY = os.environ.get('HEDRA_API_KEY')

# Business configuration
BUSINESS_NAME = "Divine Talks with Zahrah Imani"
ADMIN_EMAIL = "tkophotography2004@gmail.com"
TIKTOK_URL = "https://www.tiktok.com/@tkotalks"
TIMEZONE = pytz.timezone('US/Central')  # CST timezone

# Session pricing (in cents for Stripe)
SESSION_TYPES = {
    'quick_guidance': {
        'name': 'Quick Guidance',
        'duration': 10,
        'price': 1700,  # $17.00
        'description': 'Brief spiritual insights for immediate clarity and daily guidance'
    },
    'deep_dive': {
        'name': 'Deep Dive Session', 
        'duration': 30,
        'price': 9700,  # $97.00
        'description': 'Comprehensive spiritual exploration with ancestral wisdom and transformation guidance'
    },
    'intensive_healing': {
        'name': 'Intensive Healing',
        'duration': 60, 
        'price': 29700,  # $297.00
        'description': 'Complete spiritual realignment including soul work, trauma clearing, and deep healing'
    }
}

# Initialize database and login manager
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models and routes
from app.models import *
from app.routes import *

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database and create admin user
def init_db():
    with app.app_context():
        db.create_all()

        # Create admin user if doesn't exist
        admin = User.query.filter_by(username='tina_admin').first()
        if not admin:
            admin = User(
                username='tina_admin',
                email=ADMIN_EMAIL,
                first_name='Tina',
                last_name='',
                password_hash=generate_password_hash('DivineTalks2024!'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Admin user created: tina_admin / DivineTalks2024!")

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
