# app/cli.py
import os
import subprocess
import logging
import click
from flask import current_app
from .models import db

logger = logging.getLogger("FinanceLogger")

def register_cli_commands(app):

    @app.cli.command("update_db")
    def update_db():
        # Initialize, migrate, and upgrade the database
        migrations_path = os.path.join(
            os.path.dirname(current_app.root_path),
            "migrations"
        )

        if not os.path.exists(migrations_path):
            logger.info("Migrations folder not found, initializing.")
            result = subprocess.run(
                ["flask", "db", "init"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                logger.error(result.stderr)
                return

        message = click.prompt("Migration message")
        logger.info("Migration message: %s", message)
        
        migrate = subprocess.run(
            ["flask", "db", "migrate", "-m", message],
            capture_output=True,
            text=True
        )
        if migrate.returncode != 0:
            logger.error(migrate.stderr)
            return
        upgrade = subprocess.run(
            ["flask", "db", "upgrade"],
            capture_output=True,
            text=True
        )
        if upgrade.returncode != 0:
            logger.error(upgrade.stderr)

    @app.cli.command("backup")
    def backup():
        from .file_functions import backup_db_and_logs
        if backup_db_and_logs():
            logger.info("Db and logs backed up successfully from cli")
            return
        logger.warning("Failed to backup db and logs from cli")

    @app.cli.command("new_log")
    def new_log():
        from .file_functions import make_new_log_file
        if make_new_log_file(): 
            logger.info("New log file made successfully from cli")
            return
        logger.warning("Failed to make new log file from cli")