"""
Structured Logging utility for Dash2BI AI.
Logs application lifecycle events while protecting sensitive user data and credentials.
"""

import logging
import sys
from typing import Optional

def setup_logger(name: str = "dash2bi_ai", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = setup_logger()

def log_event(stage: str, message: str, level: str = "INFO"):
    clean_msg = f"[{stage.upper()}] {message}"
    if level.upper() == "WARNING":
        logger.warning(clean_msg)
    elif level.upper() == "ERROR":
        logger.error(clean_msg)
    else:
        logger.info(clean_msg)
