#  Weather Data Pipeline

A Python-based ETL pipeline that **fetches** real-time weather forecasts from the [Open-Meteo API](https://open-meteo.com/), **transforms** the data (cleaning, categorization, validation), and  **loads** it into **Google BigQuery**.

---

## Project Structure

```
tacheon_assessment/
├── .env                          # Environment variables (GCP project, credentials)
├── .gitignore
├── requirements.txt              # Python dependencies
├── README.md
│
├── task1/                        # (Reserved for Task 1)
│
└── task2/                        # Weather ETL Pipeline
    ├── src/
    │   ├── config.json           # City coordinates & API field config
    │   ├── pipeline/
    │   │   └── main.py           # Full pipeline entry point (fetch → transform → load)
    │   ├── loaders/
    │   │   ├── fetch.py          # Fetches raw weather data from Open-Meteo API
    │   │   └── bigquery_loader.py# Loads processed CSVs into BigQuery
    │   └── Cleaners/
    │       └── transform.py      # Cleans & transforms raw JSON → CSV
    ├── utils/
    │   └── helpers.py            # Logger utility
    ├── data/
    │   ├── raw/                  # Raw JSON responses (auto-created per run)
    │   └── processed/            # Cleaned CSV files (auto-created per run)
    ├── logs/                     # Pipeline run logs (auto-created)
    ├── notebooks/
    │   ├── fetch.ipynb           # Interactive fetch notebook
    │   └── transform.ipynb       # Interactive transform notebook
    ├── queries.sql               # BigQuery analytical queries
    └── credentials/              # GCP service account key (gitignored)
```

---

## Prerequisites

- **Python 3.9+** installed ([Download](https://www.python.org/downloads/))
- **pip** (comes with Python)
- **GCP Service Account Key** *(only if loading data into BigQuery)*

---

## Setup & Execution (Virtual Environment)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/samba-siva-rao-bandreddi/tacheon_assessment.git
cd tacheon_assessment
```

### Step 2 — Create a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
```

**macOS / Linux:**
```bash
python3 -m venv venv
```

### Step 3 — Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

> You should see `(venv)` at the beginning of your terminal prompt.

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5 — Configure Environment Variables

Create a `.env` file in the project root (if not already present):

```env
GCP_PROJECT_ID=your-gcp-project-id
DATASET_NAME=weather_dataset
GOOGLE_APPLICATION_CREDENTIALS=task2/credentials/service-account.json
```

> **Note:** BigQuery upload is **optional**. If credentials are missing, the pipeline still runs and saves data as local CSVs.

### Step 6 — Run the Pipeline

```bash
python task2/src/pipeline/main.py
```

This runs the full ETL pipeline:

| Step | Description |
|------|-------------|
| **Fetch** | Calls the Open-Meteo API for 5 cities (Chennai, Hyderabad, Bengaluru, Mumbai, Itanagar) |
| **Transform** | Cleans raw JSON → structured CSV with categories (temp, wind, humidity) |
| **Load** | Uploads processed data to BigQuery *(skipped if no credentials)* |

### Step 7 — Deactivate the Virtual Environment (when done)

```bash
deactivate
```

---

## Running Individual Steps

You can also run the **fetch** step independently:

```bash
python task2/src/loaders/fetch.py
```

---

## Output

After a successful run, you'll find:

| Output | Location |
|--------|----------|
| Raw JSON files | `task2/data/raw/<timestamp>/` |
| Processed CSVs | `task2/data/processed/<timestamp>/` |
| Run log | `task2/logs/<timestamp>.log` |

---

## BigQuery Queries

Once data is loaded into BigQuery, run the analytical queries from [`queries.sql`](task2/queries.sql):

1. **City-Level Weather Summary** — Average temp, max wind, avg humidity per city
2. **Top 10 Hottest Hours** — Most extreme heat events across all cities

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `requests` | HTTP calls to Open-Meteo API |
| `pandas` | Data manipulation & transformation |
| `python-dotenv` | Load `.env` variables |
| `matplotlib` | Data visualization (notebooks) |
| `google-cloud-bigquery` | BigQuery client |
| `pyarrow` | BigQuery DataFrame upload support |
| `db-dtypes` | BigQuery date/time type support |
