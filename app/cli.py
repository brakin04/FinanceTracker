# app/cli.py
import os
import subprocess
import logging
import click
from flask import current_app
from .models import db

logger = logging.getLogger("FinanceLogger")

def register_cli_commands(app):
    """Attach CLI commands to the Flask app."""

    @app.cli.command("update_db")
    def update_db():
        """Initialize, migrate, and upgrade the database."""
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



