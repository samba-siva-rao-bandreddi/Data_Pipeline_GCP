import os
import json
import pandas as pd


def run_transform(raw_dir, processed_dir, logger, rel_path):
    """
    Read raw JSON files, clean/transform into DataFrames, save as CSVs.
    Logic matches transform.ipynb notebook exactly.
    """
    # Find all raw JSON files in the run directory
    raw_files = [f for f in os.listdir(raw_dir) if f.endswith("_raw.json")]

    if not raw_files:
        logger.warning(f"No raw JSON files found in {rel_path(raw_dir)}")
        return False

    logger.info(f"=== TRANSFORM STEP START ===")
    logger.info(f"Found {len(raw_files)} raw file(s) to process")

    os.makedirs(processed_dir, exist_ok=True)

    for raw_file in raw_files:
        # Derive city name from filename (e.g., chennai_raw.json -> Chennai)
        city_name = raw_file.replace("_raw.json", "").capitalize()
        raw_path = os.path.join(raw_dir, raw_file)

        logger.info(f"--- Transforming: {city_name} ---")

        try:
            # Step 1: Read raw JSON
            with open(raw_path, "r") as f:
                data = json.load(f)
            logger.info(f"Loaded {rel_path(raw_path)}")

            # Step 2: Build DataFrame with renamed columns + metadata
            df = pd.DataFrame({
                "hour": data["hourly"]["time"],
                "city": city_name,
                "latitude": data["latitude"],
                "longitude": data["longitude"],
                "temp": data["hourly"]["temperature_2m"],
                "wind_speed": data["hourly"]["wind_speed_10m"],
                "humidity": data["hourly"]["relative_humidity_2m"]
            })
            logger.info(f"Built DataFrame: {len(df)} rows, {len(df.columns)} columns")

            # Step 3: Parse datetime
            df["hour"] = pd.to_datetime(df["hour"])

            # Step 4: Check nulls
            null_count = df.isnull().sum().sum()
            has_nulls = df.isnull().values.any()
            logger.info(f"Null check: {null_count} null(s) found, has_nulls={has_nulls}")

            # Step 5: Extract date and hour
            df["date"] = df["hour"].dt.date
            df["hour"] = df["hour"].dt.hour

            # Step 6: Add temp_category
            df["temp_category"] = pd.cut(
                df["temp"],
                bins=[0, 25, 32, 38, 100],
                labels=["Cool", "Medium", "Hot", "Extreme Hot"]
            )

            # Step 7: Add wind_category
            df["wind_category"] = pd.cut(
                df["wind_speed"],
                bins=[0, 5, 10, 15, 100],
                labels=["Low", "Moderate", "High", "Very High"]
            )

            # Step 8: Add humidity_category
            df["humidity_category"] = pd.cut(
                df["humidity"],
                bins=[0, 30, 60, 80, 100],
                labels=["Low", "Moderate", "High", "Very High"]
            )

            logger.info(f"Added categories: temp_category, wind_category, humidity_category")

            # Step 9: Drop duplicates
            before_dedup = len(df)
            df.drop_duplicates(subset=["date", "hour", "city"], inplace=True)
            after_dedup = len(df)
            if before_dedup != after_dedup:
                logger.warning(f"Dropped {before_dedup - after_dedup} duplicate row(s)")
            else:
                logger.info(f"No duplicates found")

            # Step 10: Validate data ranges
            try:
                assert df["humidity"].between(0, 100).all(), "Invalid humidity values found"
                assert df["wind_speed"].ge(0).all(), "Invalid wind speed values found"
                assert df["temp"].between(-50, 60).all(), "Invalid temperature values found"
                logger.info(f"Validation passed: all values in valid ranges")
            except AssertionError as e:
                logger.warning(f"Validation issue: {e}")

            # Step 11: Forward fill missing values
            df["temp"] = df["temp"].ffill()
            df["humidity"] = df["humidity"].ffill()
            df["wind_speed"] = df["wind_speed"].ffill()

            logger.info(f"Cleaned: {len(df)} rows, columns: {list(df.columns)}")

            # Step 12: Save as CSV
            csv_filename = f"{city_name.lower()}.csv"
            csv_path = os.path.join(processed_dir, csv_filename)
            df.to_csv(csv_path, index=False)

            logger.info(f"{city_name} CSV saved -> {rel_path(csv_path)}")

        except Exception as e:
            logger.error(f"Failed to transform {city_name}: {e}")

    logger.info(f"=== TRANSFORM STEP COMPLETE === -> {rel_path(processed_dir)}")
    return True
