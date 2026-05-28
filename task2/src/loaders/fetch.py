import os
import sys
import json
from datetime import datetime
import requests

# Resolve paths dynamically
script_dir = os.path.dirname(os.path.abspath(__file__))
task2_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))
project_dir = os.path.abspath(os.path.join(task2_dir, ".."))

# Add task2 directory to sys.path for imports
if task2_dir not in sys.path:
    sys.path.insert(0, task2_dir)

from utils.helpers import get_logger

# Initial logger (console only, file handler added later)
logger = get_logger(__name__)

API_URL = "https://api.open-meteo.com/v1/forecast"


def rel_path(abs_path):
    """Convert absolute path to relative path from project root."""
    return os.path.relpath(abs_path, project_dir)


def fetch_weather(city_name, latitude, longitude, hourly_fields):
    """
    Fetch weather forecast from Open-Meteo API for a single city.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(hourly_fields)
    }

    try:
        logger.info(f"Hitting API: {API_URL} | lat={latitude}, long={longitude}")

        response = requests.get(
            url=API_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        logger.info(f"API response OK (status {response.status_code}) for {city_name}")
        return data

    except requests.exceptions.Timeout:
        logger.error(f"Request timed out for {city_name}")

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error for {city_name}: {e}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for {city_name}: {e}")

    return None


def run_fetch(config, raw_dir, _logger, _rel_path):
    """
    Fetch weather data for all cities and save raw JSONs.
    Can be called standalone or from pipeline (main.py).
    """
    global logger
    logger = _logger

    cities = config.get("cities", [])
    hourly_fields = config.get("hourly_fields", [])

    if not cities:
        logger.warning("No cities configured in config.json")
        return False

    logger.info(f"=== FETCH STEP START ===")

    for city_info in cities:
        city_name = city_info.get("name")
        latitude = city_info.get("latitude")
        longitude = city_info.get("longitude")

        if not city_name or latitude is None or longitude is None:
            logger.warning(f"Skipping invalid city entry: {city_info}")
            continue

        logger.info(f"--- Fetching: {city_name} ---")
        weather_data = fetch_weather(city_name, latitude, longitude, hourly_fields)

        if weather_data:
            filename = f"{city_name.lower()}_raw.json"
            filepath = os.path.join(raw_dir, filename)

            try:
                with open(filepath, "w") as f:
                    json.dump(weather_data, f, indent=4)
                logger.info(f"{city_name} data saved -> {_rel_path(filepath)}")
            except Exception as e:
                logger.error(f"Failed to save data for {city_name}: {e}")
        else:
            logger.error(f"No data saved for {city_name} due to fetch failure")

    logger.info(f"=== FETCH STEP COMPLETE === -> {_rel_path(raw_dir)}")
    return True


def main():
    """
    Standalone entry point — runs fetch with its own timestamp and logging.
    """
    global logger

    # Load configuration
    config_path = os.path.join(task2_dir, "src", "config.json")
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        logger.info(f"Loaded config from {rel_path(config_path)}")
    except Exception as e:
        logger.error(f"Failed to load config from {rel_path(config_path)}: {e}")
        return

    # Generate timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create raw run directory
    raw_dir = os.path.join(task2_dir, "data", "raw", timestamp)
    os.makedirs(raw_dir, exist_ok=True)

    # Setup file logging
    log_file = os.path.join(task2_dir, "logs", f"{timestamp}.log")
    logger = get_logger(__name__, log_file=log_file)

    logger.info(f"Starting standalone fetch run: {timestamp}")
    logger.info(f"Log file: {rel_path(log_file)}")

    # Run fetch
    run_fetch(config, raw_dir, logger, rel_path)

    logger.info(f"Fetch run complete. Data folder: {rel_path(raw_dir)}")


if __name__ == "__main__":
    main()
