import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

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
from src.loaders.bigquery_loader import run_bigquery_load


def rel_path(abs_path):
    """Convert absolute path to relative path from project root."""
    return os.path.relpath(abs_path, project_dir)


def main():
    # ── 0. Load environment variables from .env ──
    env_path = os.path.join(project_dir, ".env")
    load_dotenv(env_path)

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

    # ── 7. LOAD TO BIGQUERY (optional — skips if no credentials) ──
    project_id = os.getenv("GCP_PROJECT_ID", "")
    dataset_name = os.getenv("DATASET_NAME", "")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

    # Resolve relative credentials path from project root
    if credentials_path and not os.path.isabs(credentials_path):
        credentials_path = os.path.join(project_dir, credentials_path)

    bq_ok = run_bigquery_load(
        processed_dir, project_id, dataset_name,
        credentials_path, logger, rel_path
    )

    if bq_ok:
        logger.info("Data saved to BigQuery [OK]")
    else:
        logger.info("Data saved to processed CSVs only (BigQuery skipped)")

    # ── 8. Pipeline complete ──
    logger.info(f"{'='*50}")
    logger.info(f"PIPELINE COMPLETE | Run ID: {timestamp}")
    logger.info(f"{'='*50}")


if __name__ == "__main__":
    main()
