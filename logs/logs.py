# logs.py
# Enkel logging for feilsøking og ytelsesmåling

import logging

logging.basicConfig(
    filename="../app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_info(message: str):
    """Logger informasjon."""
    logging.info(message)

def log_error(message: str):
    """Logger feil."""
    logging.error(message)

def log_warning(message: str):
    """Logger advarsler."""
    logging.warning(message)
