# Holds routes for home page, profile, dashboard, and logging info page

from flask import Blueprint, render_template, current_app, session, request, redirect, url_for, flash
from app.models import db, User
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user
from app.logging_config import savedLevel
from app.utils import get_file_content, check_dates, get_pie_chart, get_bar_graph, get_finances_by_date_range, get_total_from_query_list
from datetime import datetime
import logging
import os

main_bp = Blueprint('main', __name__)
logger = logging.getLogger("FinanceLogger")

@main_bp.route('/')
def home():
    logger.debug(f"Home function entered in main.py Session ID: {session.get('session_id')}")
    logger.info("Home page requested")

    # get README.md content
    # readme_file = get_file_content(os.getcwd() + '/README.md')

    logger.debug("Home function exited in main.py")
    return render_template('home.html')#, content=readme_file)


#-------------------------------
@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    logger.debug(f"Profile function entered in main.py with method: {request.method}")

    if request.method == 'POST':
        email = request.form['email']
        nickname = request.form['nickname']
        new_pw = request.form['new_password']
        confirm_pw = request.form['confirm_password']

        # Check for email or nickname conflicts
        if email != current_user.email:
            query = db.select(User).filter_by(email=email).filter(User.id != current_user.id).limit(1)
            if db.session.scalar(query) is not None:
                logger.warning("Profile update failed: Email already taken")
                flash("Email already taken!", "warning")
                return redirect(url_for('main.profile'))

        if nickname != current_user.nickname:
            query = db.select(User).filter_by(nickname=nickname).filter(User.id != current_user.id).limit(1)
            if db.session.scalar(query) is not None:
                logger.warning(f"Profile update failed: Nickname \"{nickname}\" already taken")
                flash("Nickname already taken!", "warning")
                return redirect(url_for('main.profile'))
            
        # Check if user wants to change password
        if new_pw and confirm_pw:
            if new_pw == confirm_pw:
                current_user.password_hash = generate_password_hash(new_pw)
                logger.info(f"Password updated for user: {current_user.nickname}")
            else:
                flash("Passwords do not match!", "danger")
                return redirect(url_for('main.profile'))
        elif new_pw and not confirm_pw:
            logger.debug("No confirm password provided")
            flash("Please confirm your new password!", "warning")
            return redirect(url_for('main.profile'))

        # Update user info
        current_user.email = email
        current_user.nickname = nickname
        db.session.commit()
        logger.info(f"Profile updated for user: {current_user.nickname}")
        flash("Profile updated successfully!", "success")
        logger.debug("Profile function exited with success in main.py")
        return redirect(url_for('main.profile'))
    
    # GET request handling
    userInfo = {'email': current_user.email, 'nickname': current_user.nickname}
    return render_template('profile.html', userInfo=userInfo)


###
### Dashboard functions
###


@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Helper to convert stored ISO strings back to datetime objects
    def get_dates(kind_data):
        s = datetime.fromisoformat(kind_data['start_date']) if kind_data.get('start_date') else None
        e = datetime.fromisoformat(kind_data['end_date']) if kind_data.get('end_date') else None
        return s, e

    # Prepare containers for charts/totals to pass to template
    processed = {"expenses": {}, "incomes": {}, "compares": {}}
    
    for kind in ['expenses', 'incomes', 'compares']:
        sess_data = session.get(f'dashboard_{kind}', {}).copy()
        if sess_data:
            start, end = get_dates(sess_data)
            
            if kind == "compares":
                i_data = get_finances_by_date_range(user_id=current_user.id, start_date=start, end_date=end, finance_type='i')
                e_data = get_finances_by_date_range(user_id=current_user.id, start_date=start, end_date=end, finance_type='e')
                sess_data['profit'] = get_total_from_query_list(i_data) - get_total_from_query_list(e_data)
            else:
                data = get_finances_by_date_range(user_id=current_user.id, start_date=start, end_date=end, finance_type=kind[0])
                sess_data['total'] = get_total_from_query_list(data)
                sess_data['category_chart'] = get_pie_chart(query_data=data, type=kind)
                sess_data['bar_graph'] = get_bar_graph(start=start, end=end, query_data=data, type=kind)
            
            processed[kind] = sess_data

    timeframes = ["None", "1 day", "3 days", "5 days", "7 days", "1 month", "6 months", "1 year", "All time"]
    return render_template('dashboard.html', 
                           expenses=processed['expenses'], 
                           incomes=processed['incomes'], 
                           compare=processed['compares'], 
                           timeframes=timeframes)


#-------------------------------
# This function is used to filter the dashboard based on user input. It takes the kind as an 
#   argument to know which filters to apply and where to store them.
@main_bp.route('/dashboard/filter', methods=['POST'])
@login_required
def filter_dashboard():
    logger.debug("filter_dashboard function entered in main.py")
    kind = request.args.get('kind').lower()

    if kind not in ['expenses', 'incomes', 'compares']:
        logger.warning(f"Invalid filter kind: {kind}")
        flash("Invalid filter type!", "warning")
        return redirect(url_for('main.dashboard'))
    
    # Clear previous filters
    session[f'dashboard_{kind}'] = {}

    # Add filters to dictionary
    timeframe = request.form['timeframe']
    form_start_date = request.form['start_date']
    form_end_date = request.form['end_date']

    timeAnswers = check_dates(timeframe=timeframe, form_start_date=form_start_date, 
                              form_end_date=form_end_date)
    
    if timeAnswers[0] == None and timeAnswers[1] == None:
        logger.debug(f"Clearing {kind} filters as per request")
        flash(f"Cleared {kind} filters!", "info")
        return redirect(url_for('main.dashboard'))

    if kind == "compares":
        incomes = get_finances_by_date_range(user_id=current_user.id, start_date=timeAnswers[0], end_date=timeAnswers[1], finance_type='i')
        expenses = get_finances_by_date_range(user_id=current_user.id, start_date=timeAnswers[0], end_date=timeAnswers[1], finance_type='e')
        iTotal = get_total_from_query_list(incomes)
        eTotal = get_total_from_query_list(expenses)

        # Add em to map
        session['dashboard_compares'] = {
            "timeframe": timeframe,
            "profit": iTotal - eTotal,
            "start_date": timeAnswers[0].strftime("%Y-%m-%d") if timeAnswers[0] else None,
            "end_date": timeAnswers[1].strftime("%Y-%m-%d") if timeAnswers[1] else None
        }
    else:
        # Add em to map
        session[f'dashboard_{kind}'] = {
            "timeframe": timeframe,
            "start_date": timeAnswers[0].strftime("%Y-%m-%d") if timeAnswers[0] else None,
            "end_date": timeAnswers[1].strftime("%Y-%m-%d") if timeAnswers[1] else None
        }
    logger.debug("filter_dashboard function exited in main.py")
    return redirect(url_for('main.dashboard'))


###
### Other routes (logging)
###

logLevel = logging.DEBUG
# ------------------------------
# Used to change the log level at runtime from the logging info page
@main_bp.route('/logging-info', methods=['GET', 'POST'])
@login_required
def logging_info():
    logger.debug(f"logging_info function entered in main.py method: {request.method}")
    # Get the handler and check if its found
    file_handler = next((h for h in logger.handlers if isinstance(h, logging.FileHandler)), None)
    # file_handler = current_app.config.get('FILE_HANDLER')

    if not file_handler:
        logger.warning("logging_info function exited (handler not found)")
        flash("Log handler not found!", "warning")
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        level = request.args.get('level').upper()

        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING
            # 'ERROR': logging.ERROR
        }

        if level not in levels:
            logger.warning("Set log level function exited (not valid level)")
        else:
            file_handler.setLevel(levels[level])
            savedLevel("POST", level)
            flash(f"Log level changed to {level}", "info")
            logger.info(f"Log level changed to {level}")
            logger.debug("Set log level function exited with success")
        return redirect(url_for('main.dashboard'))

    # Renders logging info
    log_file = get_file_content(os.getcwd() + '/logs/finance.log')
    logger.debug("logging_info function exited in main.py")
    return render_template('logging_info.html', current_level=logging.getLevelName(file_handler.level), log_file=log_file)