# Sweety Stash

A playful budgeting app where your virtual pet reacts to your spending and savings progress.

## Overview

Sweety Stash is a web-based budgeting application that gamifies personal finance management. Users can track their income and expenses while a virtual pet companion provides visual feedback based on their financial habits. The pet's mood changes based on spending patterns and savings rates, making budgeting more engaging and fun.

## Recent Changes

### November 20, 2025 - Initial Development
- Created complete Flask web application from scratch
- Implemented frontend with HTML, CSS, and vanilla JavaScript
- Built backend API endpoints for transaction management
- Created virtual pet animation system with mood states
- Configured for Replit environment with proper port and host settings

## Project Architecture

### Technology Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Session Management**: Flask sessions (server-side)
- **Deployment**: Gunicorn (production-ready)

### Project Structure
```
sweety-stash/
├── app.py                  # Main Flask application with API endpoints
├── templates/
│   └── index.html         # Main UI template
├── static/
│   ├── css/
│   │   └── style.css      # Styling and animations
│   └── js/
│       └── app.js         # Frontend logic
├── requirements.txt       # Python dependencies
├── pyproject.toml         # UV package configuration
└── replit.md             # This documentation file
```

### Key Features

1. **Transaction Management**
   - Add income and expenses
   - Categorize transactions
   - View transaction history
   - Track real-time balance

2. **Budget Tracking**
   - Set and update budget amounts
   - Monitor current balance
   - Visual statistics display

3. **Virtual Pet Companion**
   - Five mood states: happy, excited, sad, concerned, neutral
   - Reacts to spending vs. saving behavior
   - Animated with CSS (bounce, wiggle effects)
   - Provides encouraging or cautionary messages

4. **Pet Mood Logic**
   - **Excited**: Savings rate > 50%
   - **Happy**: Savings rate > 20%
   - **Neutral**: Balanced spending
   - **Concerned**: Spending exceeds income
   - **Sad**: Negative balance (debt)

### API Endpoints

- `GET /` - Main application page
- `GET /api/transactions` - Get all transactions and current state
- `POST /api/transactions` - Add new transaction
- `POST /api/budget` - Update budget amount
- `POST /api/reset` - Clear all data

### Configuration

The application is configured to run on:
- **Host**: 0.0.0.0 (required for Replit)
- **Port**: 5000 (Replit standard for webview)
- **Debug Mode**: Controlled via FLASK_ENV environment variable
- **Secret Key**: Auto-generated using Python secrets module; can be overridden with SECRET_KEY environment variable for production

#### Environment Variables
- `SECRET_KEY` (optional): Set a custom Flask session secret key for production deployments
- `FLASK_ENV` (optional): Set to 'development' to enable debug mode

### Data Storage

Currently uses Flask session storage for simplicity. Data persists during the user's session but resets when the browser session ends. Future enhancements could include:
- PostgreSQL database for persistent storage
- User authentication
- Multi-user support

## Development Notes

- The app uses session-based storage, so data is temporary
- No database setup required for basic functionality
- The pet's mood calculation runs on every API call
- Frontend uses pure JavaScript (no frameworks) for simplicity
- Responsive design works on mobile and desktop
