# 🔐 Password Strength Checker - Django Web Application

A modern, real-time password strength analyzer built with Django. This application helps users create stronger passwords by providing instant feedback on password security.

## ✨ Features

- **Real-time Analysis**: Instant password strength feedback as you type
- **Entropy Calculation**: Scientific measurement of password randomness
- **Time-to-Crack Estimation**: Shows how long it would take to crack your password
- **Visual Feedback**: Color-coded strength meter and detailed criteria checklist
- **Security-First**: Passwords are never stored or logged
- **Modern UI**: Beautiful, responsive design with smooth animations
- **Django REST API**: Clean API endpoint for password analysis

## 🎯 Password Analysis Metrics

- **Entropy bits**: Measures password randomness
- **Character pool**: Types of characters used
- **Time to crack**: Estimated cracking time at 10 billion guesses/second
- **Strength rating**: Very Weak, Weak, Medium, Strong, Very Strong
- **Security suggestions**: Actionable feedback to improve password

## 🚀 Quick Start

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Database Migrations

```bash
python manage.py migrate
```

### 3. Start Development Server

```bash
python manage.py runserver
```

### 4. Open in Browser

Navigate to: `http://127.0.0.1:8000/`

## 📁 Project Structure

```
password_checker_project/
├── password_checker/          # Main project settings
│   ├── settings.py           # Django configuration
│   ├── urls.py               # Root URL routing
│   └── wsgi.py               # WSGI config
├── checker/                   # Password checker app
│   ├── views.py              # API and page views
│   ├── urls.py               # App URL routing
│   └── tests.py              # Unit tests
├── templates/                 # HTML templates
│   └── index.html            # Main page
├── static/                    # Static files
│   ├── css/style.css         # Styles
│   └── js/main.js            # JavaScript
├── manage.py                  # Django management script
└── requirements.txt           # Python dependencies
```

## 🔌 API Usage

### Endpoint: `/api/check/`

**Method**: POST

**Request Body**:
```json
{
  "password": "MyPassword123!"
}
```

**Response**:
```json
{
  "entropy_bits": 65.27,
# 🔐 Password Strength Checker

A real-time password strength analyzer built with Django. This project provides instant, actionable feedback to help users create stronger passwords.

## ✨ Features

- Real-time password strength feedback
- Entropy calculation and time-to-crack estimation
- Color-coded strength meter and checklist guidance
- Passwords are processed in memory and not stored or logged
- Lightweight Django REST API for analysis

## 🎯 Metrics

- Entropy (bits)
- Character pool size
- Estimated time to crack (based on guesses/sec)
- Strength rating (Very Weak → Very Strong)
- Actionable feedback to improve passwords

## 🚀 Quick Start (Local)

1. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations and start the development server:

```bash
python manage.py migrate
python manage.py runserver
```

4. Open your browser at `http://127.0.0.1:8000/`

## 🚢 Quick Start (Docker)

If you prefer Docker:

```bash
docker-compose up --build -d
docker-compose exec web python manage.py migrate
```

Then visit `http://127.0.0.1:8000/`.

## 📁 Project Structure (key files)

```
./
├── checker/            # Django app that implements the password analysis
├── password_checker/   # Django project settings
├── static/             # Frontend assets (css, js)
├── templates/          # HTML templates
├── manage.py           # Django management script
└── requirements.txt    # Python dependencies
```

## 🔌 API Usage

Endpoint: `/api/check/` (POST)

Request body:

```json
{ "password": "MyPassword123!" }
```

Example response:

```json
{
   "entropy_bits": 65.27,
   "time_to_crack": "11.7 years",
   "strength": "Strong",
   "feedback": [],
   "character_pool": 94,
   "password_length": 14
}
```

cURL example:

```bash
curl -X POST http://127.0.0.1:8000/api/check/ \
   -H "Content-Type: application/json" \
   -d '{"password":"TestPass123!"}'
```

## 🧪 Tests

Run unit tests:

```bash
python manage.py test checker
```

## 🔒 Security Notes

- Passwords are processed in memory and not persisted
- Password values are not logged
- Django's CSRF protection is enabled by default

## 📊 How Strength Is Calculated

Entropy is calculated as:

$$Entropy = Length \\times \\log_2(CharacterPoolSize)$$

Recommended thresholds (configurable in code):

- Very Weak: < 28 bits
- Weak: 28–36 bits
- Medium: 36–60 bits
- Strong: 60–80 bits
- Very Strong: > 80 bits

## ⚙️ Customization

- Adjust thresholds in `checker/views.py` where strength is determined.
- Update `guesses_per_second` in code to change time-to-crack assumptions.
- Modify `static/css/style.css` to change styling.

## 🌐 Deployment (production hints)

- Set `DEBUG = False` and configure `ALLOWED_HOSTS` and `SECRET_KEY` in `password_checker/settings.py`.
- Run `python manage.py collectstatic` and serve static files via a web server.
- Use HTTPS in production.

## 🤝 Contributing

Contributions welcome — please open an issue or submit a pull request.

If you'd like, I can also add a short Docker deployment section or update any paths to match your preferred setup.
