
-- Run these in BigQuery Console after loading data



-- QUERY 1: City-Level Weather Summary (Aggregation)
-- Shows average temp, max wind, avg humidity per city

SELECT
    city,
    ROUND(AVG(temperature_c), 1)  AS avg_temp_c,
    ROUND(MAX(temperature_c), 1)  AS max_temp_c,
    ROUND(MIN(temperature_c), 1)  AS min_temp_c,
    ROUND(MAX(wind_speed_kmh), 1) AS max_wind_kmh,
    ROUND(AVG(humidity_pct), 0)   AS avg_humidity_pct
FROM
    `weather_dataset.hourly_weather`
GROUP BY
    city
ORDER BY
    avg_temp_c DESC;





-- QUERY 2: Top 10 Hottest Hours Across All Cities (Top-N)
-- Identifies the most extreme heat events in the dataset

SELECT
    city,
    date
    hour,
    temperature_c,
    humidity_pct,
    temp_category
FROM
    `weather_dataset.hourly_weather`
ORDER BY
    temperature_c DESC
LIMIT 10;




