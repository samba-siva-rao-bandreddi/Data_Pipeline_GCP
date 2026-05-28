import os
import sys
import json
from datetime import datetime

# Resolve paths dynamically
script_dir = os.path.dirname(os.path.abspath(__file__))
task2_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))
project_dir = os.path.abspath(os.path.join(task2_dir, ".."))

# Add task2 directory to sys.path for imports
if task2_dir not in sys.path:
    sys.path.insert(0, task2_dir)

from utils.helpers import get_logger
from src.loaders.fetch import run_fetch
from src.Cleaners.transform import run_transform


def rel_path(abs_path):
    """Convert absolute path to relative path from project root."""
    return os.path.relpath(abs_path, project_dir)


def main():
    # ── 1. Generate ONE timestamp for the entire pipeline run ──
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ── 2. Setup directories with shared timestamp ──
    raw_dir = os.path.join(task2_dir, "data", "raw", timestamp)
    processed_dir = os.path.join(task2_dir, "data", "processed", timestamp)
    log_file = os.path.join(task2_dir, "logs", f"{timestamp}.log")

    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    # ── 3. Setup logger (console + file) ──
    logger = get_logger("pipeline", log_file=log_file)

    logger.info(f"{'='*50}")
    logger.info(f"PIPELINE START | Run ID: {timestamp}")
    logger.info(f"{'='*50}")
    logger.info(f"Log file   : {rel_path(log_file)}")
    logger.info(f"Raw dir    : {rel_path(raw_dir)}")
    logger.info(f"Processed  : {rel_path(processed_dir)}")

    # ── 4. Load configuration ──
    config_path = os.path.join(task2_dir, "src", "config.json")
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        logger.info(f"Config loaded from {rel_path(config_path)}")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    # ── 5. FETCH step ──
    fetch_ok = run_fetch(config, raw_dir, logger, rel_path)

    if not fetch_ok:
        logger.error("Fetch step failed. Stopping pipeline.")
        return

    # ── 6. TRANSFORM step ──
    transform_ok = run_transform(raw_dir, processed_dir, logger, rel_path)

    if not transform_ok:
        logger.error("Transform step failed.")
        return

    # ── 7. Pipeline complete ──
    logger.info(f"{'='*50}")
    logger.info(f"PIPELINE COMPLETE | Run ID: {timestamp}")
    logger.info(f"{'='*50}")


if __name__ == "__main__":
    main()
