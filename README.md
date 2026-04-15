# Finance Tracker

A simple money tracking platform built by Bryan A.

---

## ✨ Features
- User Registration, Login & Logout
- Track expenses and incomes
- Dark Mode Toggle (per session)
- Protected routes using Flask-Login
- Flash messages styled with Bootstrap
- Jinja2 templating language

---

## 💻 Tech Stack
- Python 3.x
- Flask
- Flask-Login
- SQLAlchemy
- Bootstrap 5
- Jinja2

---

## ✅ How to Run Locally

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Initialize Database
```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> app.app_context().push()
>>> db.create_all()
>>> exit()
```
### 3️⃣ Run this line
```bash
export FLASK_APP=run.py
```
or the following if you are on Windows:
```bash
$env:FLASK_APP = "run.py"
```

## If you'd like to type 'r' in the command line to restart and 'q' to quit
Run this line
```bash
chmod +x start.sh
```
If that doesnt work use option 3 below

### 4️⃣ Run the App
Option 1: Run regularly
```bash
python run.py
```
or the following if using 'r' and 'q'
Option 2:
```bash
./start.sh
```
Option 3:
```bash
./start.bat
```

### 5️⃣ Visit ➤ http://127.0.0.1:5050 in your browser.

### 6️⃣ To exit the app press: crtl + c

---
To change the file logger's level, click the logging info button on the dashboard  

---
## How to run using Docker
```bash
    docker build -t finance-app .
    docker run -p 5050:5050 finance-app
```

## To update the database with schema changes
```bash
    export FLASK_APP=run.py
    flask update_db  
```

## 💡 Notes
- Passwords are securely hashed using PBKDF2
- Users can add expenses and incomes with custom categories
- Flash messages will help the user understand each action's result

---
## 🎨 UI Highlights
- Reddit-style card layouts
- Responsive design (Bootstrap 5)
- Flash messages with category styling


