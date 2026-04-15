from flask import Flask
from werkzeug.exceptions import HTTPException
from flask_login import LoginManager, current_user
from flask import render_template, request
from .models import db
from .cli import register_cli_commands
from .logging_config import setup_logger 
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime
import logging
import shutil
import os

login_manager = LoginManager()
login_manager.login_view = 'auth.login' # maybe main.login
logger = logging.getLogger("FinanceLogger")

def create_app(test_config=None):
    app = Flask(__name__)
    if test_config:
        app.config.from_object(test_config)
        logger = setup_logger("tests.log", logging.DEBUG)
    else:
        app.config['SECRET_KEY'] = 'super-secret-key'
        if os.environ.get("DOCKER") == "1":
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////instance/finance.db'
        else:
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['DEBUG'] = True
        logger = setup_logger("finance.log", logging.INFO)
    app.logger = logger
    register_cli_commands(app)
    logger.info("Finance program started") 

    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    CORS(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        logger.debug(f"load_user called with ID: {user_id}")
        return User.query.get(int(user_id))

    from .routes import finance_bp, auth_bp, main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(main_bp)
    # app.register_blueprint(status_api)

    @app.errorhandler(HTTPException)
    def handle_internal_error(error):
        logger.error(f"HTTP {error.code} error on {request.path} for '{current_user.nickname}': {error}")
        description = error.description if error.description else None
        return render_template("error.html", errorNumber=error.code, description=description), error.code

    @app.errorhandler(Exception)
    def handle_error(error):
        logger.critical(f"Unexpected critical error on {request.path}: {error}", exc_info=True)
        return render_template("error.html", errorNumber=500, description=None), 500

    @app.before_request
    def log_request():
        logger.info(f"Request: {request.method} {request.path}")

    @app.after_request
    def log_response(response):
        logger.info(f"{request.method} {request.path} returned {response.status}")
        return response

    return app

import atexit
# Backup database and log exit
def log_and_db_backup():
    logger.critical("Finance program exited unexpectedly or was terminated.")
    # if os.environ.get('TESTING') == 'True':
    #     logger.info("In testing environment. Skipping backup.")
    #     return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    try:
        source = os.path.join(base_dir, 'instance', 'finance.db')
        backup_dir = os.path.join(base_dir, 'backups', 'instance')
        os.makedirs(backup_dir, exist_ok=True)
        dest = os.path.join(backup_dir, f"backup_{timestamp}.db")
        shutil.copy2(source, dest)
        logger.info(f"Database backed up to {dest}")
    except Exception as e:
        logger.error(f"DB Backup failed: {e}")
    try:
        source = os.path.join(base_dir, 'logs', 'finance.log')
        backup_dir = os.path.join(base_dir, 'backups', 'logs')
        os.makedirs(backup_dir, exist_ok=True)
        dest = os.path.join(backup_dir, f"backup_{timestamp}.log")
        shutil.copy2(source, dest)
        logger.info(f"Logs backed up to {dest}")
    except Exception as e:
        logger.error(f"Log Backup failed: {e}")

atexit.register(log_and_db_backup)