# Divine Talks with Zahrah Imani

A complete spiritual guidance platform built for Tina, featuring real-time AI avatar sessions powered by Hedra and secure payment processing through Stripe.

## Features

- **Real-time AI Avatar Sessions**: Powered by Hedra's cutting-edge technology
- **Secure Payment Processing**: Stripe integration for safe transactions
- **Mobile-Optimized Design**: Perfect for TikTok audience
- **CST Timezone Support**: Handles Tina's Central Standard Time schedule
- **Admin Dashboard**: Complete revenue tracking and booking management
- **Responsive Design**: Works beautifully on all devices

## Quick Start

1. **Clone or download this repository**
2. **Create Railway account**: Go to [railway.app](https://railway.app)
3. **Deploy to Railway**: Connect your GitHub repo or deploy directly
4. **Set environment variables**: Copy values from `.env.example`
5. **Add PostgreSQL**: Add Railway's PostgreSQL service
6. **Go live!**: Your site will be available at `yourapp.railway.app`

## Environment Variables

Set these in Railway's environment variables section:

- `FLASK_SECRET_KEY`: Generate a secure random key
- `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key
- `STRIPE_SECRET_KEY`: Your Stripe secret key  
- `HEDRA_API_KEY`: Your Hedra AI API key
- `ADMIN_PASSWORD`: Password for admin access (default: DivineTalks2024!)

Railway will automatically provide `DATABASE_URL` when you add PostgreSQL.

## Session Types & Pricing

- **Quick Insight**: 15 minutes - $17
- **Deep Reading**: 45 minutes - $97  
- **Soul Transformation**: 90 minutes - $297

## Schedule

- **Weekdays**: 5:30 PM - 10:00 PM CST
- **Weekends**: 8:00 AM - 10:00 PM CST

## Admin Access

- **URL**: `/admin`
- **Username**: `tina_admin`
- **Password**: `DivineTalks2024!` (change this!)

## Support

For technical support, contact: tkophotography2004@gmail.com

## Built With

- Flask (Python web framework)
- PostgreSQL (Database)
- Stripe (Payment processing)
- Hedra AI (Avatar technology)
- Bootstrap 5 (Responsive design)
- Railway (Hosting platform)

---

Built with ✨ for Tina's spiritual guidance business
