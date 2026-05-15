# cs1060-hw4

This repository contains the Homework 4 implementation for cs1060.

## Files

- `csv_to_sqlite.py`: converts a CSV file with a header row into a SQLite database file.
- `app.py`: Flask API prototype exposing the `/county_data` endpoint.
- `requirements.txt`: required Python packages.
- `.gitignore`: ignores generated files and caches.
- `link.txt`: placeholder API endpoint URL.

## Usage

1. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

2. Create the SQLite database from a CSV file:

```bash
python3 csv_to_sqlite.py data.db zip_county.csv
python3 csv_to_sqlite.py data.db county_health_rankings.csv
```

3. Run the API locally:

```bash
python3 app.py
```

4. Send a POST request to `/county_data` with JSON body:

```json
{
  "zip": "02138",
  "measure_name": "Adult obesity"
}
```

Alternatively, use GET query parameters:

```
https://cs1060-hw4-eight.vercel.app/county_data?zip=02138&measure_name=Adult%20obesity
```

The deployed endpoint is: `https://cs1060-hw4-eight.vercel.app/county_data`

## Notes

- The `csv_to_sqlite.py` script creates a table named after the CSV filename without its extension.
- The API uses parameterized SQL queries to avoid injection.
- `link.txt` contains the endpoint URL for the deployed API.
