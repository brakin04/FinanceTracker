from app import create_app
from app.models import db
import logging

app = create_app()
logger = logging.getLogger("FinanceLogger")      

if __name__ == '__main__':
    logger.info("Starting Finance application")
    try:
        # Check installation of all parameters
        with app.app_context():
            db.create_all()
        host = "0.0.0.0"
        port = 5050
        print(f"Flask app is running at: http://127.0.0.1:{port}")
        app.run(debug=False, host=host, port=port, use_reloader=False)
    except Exception as e:
        logger.critical(f"Application crashed: {e}")
    finally:
        logger.info("Finance application stopped")