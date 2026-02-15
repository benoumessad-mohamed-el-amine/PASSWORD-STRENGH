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
  "time_to_crack": "11.7 years",
  "strength": "Strong",
  "feedback": [],
  "character_pool": 94,
  "password_length": 14
}
```

### Example with cURL:

```bash
curl -X POST http://127.0.0.1:8000/api/check/ \
  -H "Content-Type: application/json" \
  -d '{"password":"TestPass123!"}'
```

### Example with Python:

```python
import requests

response = requests.post(
    'http://127.0.0.1:8000/api/check/',
    json={'password': 'TestPass123!'}
)
print(response.json())
```

## 🧪 Running Tests

```bash
python manage.py test checker
```

## 🔒 Security Features

- **No Storage**: Passwords are processed in memory and never stored
- **No Logging**: Password values are never logged
- **CSRF Protection**: Enabled by default in Django
- **Input Validation**: Server-side validation of all inputs
- **Error Handling**: Graceful handling of invalid requests

## 📊 Password Strength Criteria

The application evaluates passwords based on:

1. **Character Diversity**:
   - Lowercase letters (a-z)
   - Uppercase letters (A-Z)
   - Numbers (0-9)
   - Symbols (!@#$%^&*)

2. **Length**: Minimum 8 characters recommended

3. **Entropy**: Calculated using the formula:
   ```
   Entropy = Length × log₂(Character Pool Size)
   ```

4. **Strength Ratings**:
   - Very Weak: < 28 bits
   - Weak: 28-36 bits
   - Medium: 36-60 bits
   - Strong: 60-80 bits
   - Very Strong: > 80 bits

## 🎨 Customization

### Change Strength Thresholds

Edit `checker/views.py`:

```python
if entropy < 28:
    strength = "Very Weak"
elif entropy < 36:
    strength = "Weak"
# ... modify as needed
```

### Update Guesses Per Second

Edit the `guesses_per_second` variable in `views.py`:

```python
guesses_per_second = 10_000_000_000  # Adjust this value
```

### Customize Styling

Edit `static/css/style.css` to change colors, fonts, and layout.

## 🌐 Deployment

### For Production:

1. **Update settings.py**:
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com']
   SECRET_KEY = 'your-secure-secret-key'
   ```

2. **Collect static files**:
   ```bash
   python manage.py collectstatic
   ```

3. **Use production server**:
   ```bash
   pip install gunicorn
   gunicorn password_checker.wsgi:application
   ```

4. **Set up HTTPS** (required for production)

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## 📧 Support

For questions or issues, please open an issue on the repository.

---

**Note**: This tool is for educational purposes. Always use strong, unique passwords for each of your accounts and consider using a password manager.
