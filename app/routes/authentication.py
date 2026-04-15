# Holds all routes related to authentication (register, login, logout)

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger("FinanceLogger")

security_questions = ["What is your hometown?", "What was the name of your first pet?", "What is your mother's maiden name?"]
# ------------------------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    logger.debug(f"Register function entered in routes.py method: {request.method}")
    logger.info("Registration attempt initiated")
    logger.debug(f"Session ID: {session.get('session_id')}")
    if request.method == 'POST':
        email = request.form['email']
        nickname = request.form['nickname']
        password = request.form['password']
        answer1 = request.form['answer1']
        answer2 = request.form['answer2']
        answer3 = request.form['answer3']
        # role = request.form.get('role') or 'user'

        # Check for existing email and nickname
        if db.session.scalar(db.select(User).filter_by(email=email).limit(1)):
            logger.warning("Registration failed: Email already taken")
            logger.debug("Register function exited with failure in routes.py")
            flash("Email already taken!", "warning")
            return redirect(url_for('auth.register'))

        if db.session.scalar(db.select(User).filter_by(nickname=nickname).limit(1)):
            logger.warning("Registration failed: Nickname already taken")
            logger.debug("Register function exited with failure in routes.py")
            flash("Nickname already taken!", "warning")
            return redirect(url_for('auth.register'))

        # Hash password, add user data to db
        hashed_password = generate_password_hash(password)
        user = User(email=email, nickname=nickname, password=hashed_password, security_answers=[answer1, answer2, answer3])#, role=role)
        db.session.add(user)
        db.session.commit()
        logger.debug(f"User {nickname} registered in database")
        logger.info(f"New user registered: {nickname}")

        flash("Registration successful! Please login.", "success")
        logger.debug("Register function exited with success in routes.py")
        return redirect(url_for('auth.login'))
    
    logger.debug("Register function exited from GET request in routes.py")
    return render_template('register.html', security_questions=security_questions)


# ------------------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    logger.debug(f"Login function entered in routes.py method: {request.method}")
    if request.method == 'POST':
        logger.info("Login attempt")
        logger.debug(f"Session ID: {session.get('session_id')}")
        identity = request.form['identity']
        password = request.form['password']

        # Search for user using nickname / email
        user = db.session.scalar(db.select(User).filter((User.email == identity) | (User.nickname == identity)))

        # Make sure the password matches
        if user and check_password_hash(user.password, password):
            login_user(user)
            logger.info(f"Authentication success for user: {user.nickname}")
            flash("Welcome back!", "success")
            logger.debug("Login function exited with success as user in routes.py")
            return redirect(url_for('main.dashboard'))

        else:
            logger.warning(f"Authentication failure for: {identity}")
            flash("Invalid credentials, try again.", "warning")
            logger.debug("Login function exited with authentication failure in routes.py")
            return redirect(url_for('auth.login'))

    logger.debug("Login function exited from GET request in routes.py")
    return render_template('login.html')


#-------------------------------
@auth_bp.route('/login/security', methods=['GET', 'POST'])
def login_security():
    logger.debug(f"Login security function entered in routes.py method: {request.method}")
    if request.method == 'POST':
        email = request.form['email']
        nickname = request.form['nickname']
        security_question = request.form['security_question']
        security_answer = request.form['security_answer']

        # Search for user info matching what was given
        user = db.session.scalar(db.select(User).filter_by(nickname=nickname, email=email))
        logger.debug(f"User found for security question: {user.nickname if user else 'None'}")
        
        # Check security question answer
        if user and user.security_answers[security_questions.index(security_question)].lower() == security_answer.lower():
            login_user(user)
            logger.info(f"Security question authentication success for user: {user.nickname}")
            flash("Welcome back! I reccomend changing your password.", "success")
            logger.debug("Login security function exited with success as user in routes.py")
            return redirect(url_for('main.profile'))
        else:
            logger.warning(f"Security question authentication failure for: {nickname} email: {email}")
            flash("Invalid credentials", "warning")
            logger.debug("Login security function exited with authentication failure in routes.py")
            return redirect(url_for('auth.login_security'))

    logger.debug("Login security function exited from GET request in routes.py")
    return render_template('login_security.html', security_questions=security_questions)


# ------------------------------
@auth_bp.route('/logout')
@login_required
def logout():
    logger.debug("Logout function entered in routes.py")
    logger.info(f"User logged out: {current_user.nickname}")
    logout_user()
    flash("You have been logged out.", "info")
    logger.debug("Logout function exited in routes.py")

    return redirect(url_for('auth.login'))