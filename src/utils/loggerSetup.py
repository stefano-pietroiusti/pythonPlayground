import os
import logging
from datetime import datetime
from time import sleep
import json

# --- Configuration ---
# --- Load external config ---
config_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(config_path, "r") as f:
    CONFIG = json.load(f)

DATA_DIR = CONFIG["DATA_DIR"]
LOG_FILE = CONFIG["LOG_FILE"]

# --- Ensure directories exist ---
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# --- Reset log file ---
with open(LOG_FILE, "w") as f:
    f.write("")  # Clear contents

# --- Setup logging ---
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def main():
    try:
        logging.info("Starting CRMDSL")

    except Exception as e:
        logging.error(e)
        return 0


if __name__ == "__main__":
    main()
