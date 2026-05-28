import os
import glob
import pandas as pd
from google.cloud import bigquery


# BigQuery schema — explicit types for every column
BQ_SCHEMA = [
    bigquery.SchemaField("city", "STRING", mode="REQUIRED",
                         description="City name"),
    bigquery.SchemaField("latitude", "FLOAT64", mode="REQUIRED",
                         description="Latitude coordinate"),
    bigquery.SchemaField("longitude", "FLOAT64", mode="REQUIRED",
                         description="Longitude coordinate"),
    bigquery.SchemaField("date", "DATE", mode="REQUIRED",
                         description="Forecast date"),
    bigquery.SchemaField("hour", "INT64", mode="REQUIRED",
                         description="Hour of day (0-23)"),
    bigquery.SchemaField("temperature_c", "FLOAT64", mode="REQUIRED",
                         description="Temperature in Celsius"),
    bigquery.SchemaField("wind_speed_kmh", "FLOAT64", mode="REQUIRED",
                         description="Wind speed in km/h"),
    bigquery.SchemaField("humidity_pct", "INT64", mode="REQUIRED",
                         description="Relative humidity percentage"),
    bigquery.SchemaField("temp_category", "STRING", mode="NULLABLE",
                         description="Cool / Medium / Hot / Extreme Hot"),
    bigquery.SchemaField("wind_category", "STRING", mode="NULLABLE",
                         description="Low / Moderate / High / Very High"),
    bigquery.SchemaField("humidity_category", "STRING", mode="NULLABLE",
                         description="Low / Moderate / High / Very High"),
]

# Rename mapping: CSV column -> BigQuery column
COLUMN_RENAME = {
    "temp": "temperature_c",
    "wind_speed": "wind_speed_kmh",
    "humidity": "humidity_pct",
}

TABLE_NAME = "hourly_weather"


def check_credentials(credentials_path, logger):
    """
    Verify that the service account key file exists.
    Returns True if credentials are available, False otherwise.
    """
    if not credentials_path:
        logger.warning("GOOGLE_APPLICATION_CREDENTIALS not set in .env")
        return False

    if not os.path.isfile(credentials_path):
        logger.warning(
            f"Credentials file not found: {credentials_path}"
        )
        return False

    logger.info(f"Credentials found: {credentials_path}")
    return True


def load_and_prepare(processed_dir, logger, rel_path):
    """
    Read all CSVs from processed_dir, concatenate, rename columns,
    and cast to proper types for BigQuery.
    """
    csv_files = sorted(glob.glob(os.path.join(processed_dir, "*.csv")))

    if not csv_files:
        logger.warning(f"No CSV files found in {rel_path(processed_dir)}")
        return None

    frames = []
    for csv_path in csv_files:
        df = pd.read_csv(csv_path)
        logger.info(
            f"Read {os.path.basename(csv_path)}: {len(df)} rows"
        )
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    logger.info(f"Combined DataFrame: {len(combined)} rows from {len(frames)} files")

    # Rename columns to self-documenting names
    combined.rename(columns=COLUMN_RENAME, inplace=True)

    # Cast types for BigQuery compatibility
    combined["date"] = pd.to_datetime(combined["date"]).dt.date
    combined["hour"] = combined["hour"].astype(int)
    combined["humidity_pct"] = combined["humidity_pct"].astype(int)

    # Convert category columns from pandas Categorical to plain string
    for col in ["temp_category", "wind_category", "humidity_category"]:
        combined[col] = combined[col].astype(str)

    logger.info(f"Columns: {list(combined.columns)}")
    return combined


def upload_to_bigquery(df, project_id, dataset_name, logger):
    """
    Upload DataFrame to BigQuery using batch load (Sandbox-compatible).
    Uses WRITE_TRUNCATE so re-runs are safe and idempotent.
    """
    client = bigquery.Client(project=project_id)
    table_id = f"{project_id}.{dataset_name}.{TABLE_NAME}"

    job_config = bigquery.LoadJobConfig(
        schema=BQ_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    logger.info(f"Uploading {len(df)} rows to {table_id} ...")

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  # Wait for completion

    # Verify
    table = client.get_table(table_id)
    logger.info(
        f"Upload complete: {table.num_rows} rows in {table_id}"
    )
    return True


def run_bigquery_load(processed_dir, project_id, dataset_name,
                      credentials_path, logger, rel_path):
    """
    Main entry point for the BigQuery load step.
    Returns True if data was uploaded, False if skipped (no credentials).
    """
    logger.info("=== BIGQUERY LOAD STEP START ===")

    # Check credentials — skip gracefully if missing
    if not check_credentials(credentials_path, logger):
        logger.info(
            "BigQuery upload SKIPPED — no valid credentials. "
            "Data is still saved in processed CSVs."
        )
        return False

    # Set credentials for the Google Cloud client
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

    # Load and prepare data
    df = load_and_prepare(processed_dir, logger, rel_path)
    if df is None:
        logger.error("No data to upload.")
        return False

    # Upload to BigQuery
    try:
        upload_to_bigquery(df, project_id, dataset_name, logger)
        logger.info("=== BIGQUERY LOAD STEP COMPLETE ===")
        return True

    except Exception as e:
        logger.error(f"BigQuery upload failed: {e}")
        return False
