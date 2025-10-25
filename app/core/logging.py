import logging
import sys
from typing import Any

# Create logger
logger = logging.getLogger("lead_management")
logger.setLevel(logging.INFO)

# Create console handler and set level to debug
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add formatter to console handler
console_handler.setFormatter(formatter)

# Add console handler to logger
logger.addHandler(console_handler)

def get_logger() -> Any:
    return logger