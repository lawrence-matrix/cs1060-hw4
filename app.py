import os
import re
import sqlite3
from flask import Flask, abort, jsonify, request

app = Flask(__name__)
DATABASE_PATH = os.environ.get("DATA_DB", "data.db")

ALLOWED_MEASURES = {
    "Violent crime rate",
    "Unemployment",
    "Children in poverty",
    "Diabetic screening",
    "Mammography screening",
    "Preventable hospital stays",
    "Uninsured",
    "Sexually transmitted infections",
    "Physical inactivity",
    "Adult obesity",
    "Premature Death",
    "Daily fine particulate matter",
}

ZIP_REGEX = re.compile(r"^\d{5}$")


def get_db_connection():
    if not os.path.exists(DATABASE_PATH):
        raise FileNotFoundError(f"Database file not found: {DATABASE_PATH}")
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/county_data", methods=["POST"])
def county_data():
    if not request.is_json:
        abort(400, description="Request body must be JSON")

    data = request.get_json()
    if not isinstance(data, dict):
        abort(400, description="Request JSON must be an object")

    if data.get("coffee") == "teapot":
        abort(418, description="I'm a teapot")

    if "zip" not in data or "measure_name" not in data:
        abort(400, description="Missing required fields: zip and measure_name")

    zip_code = data["zip"]
    if isinstance(zip_code, int):
        zip_code = f"{zip_code:05d}"
    elif isinstance(zip_code, str):
        zip_code = zip_code.strip()
    else:
        abort(400, description="zip must be a 5-digit string or integer")

    if not ZIP_REGEX.match(zip_code):
        abort(400, description="zip must be a 5-digit string")

    measure_name = data["measure_name"]
    if not isinstance(measure_name, str):
        abort(400, description="measure_name must be a string")
    measure_name = measure_name.strip()

    if measure_name not in ALLOWED_MEASURES:
        abort(400, description="measure_name is not valid")

    query = """
        SELECT chr.*
        FROM county_health_rankings AS chr
        JOIN zip_county AS zc
          ON zc.county_code = chr.county_code
         AND zc.default_state = chr.state
        WHERE zc.zip = ?
          AND chr.measure_name = ?
    """

    try:
        conn = get_db_connection()
    except FileNotFoundError as exc:
        abort(500, description=str(exc))

    with conn:
        cursor = conn.execute(query, (zip_code, measure_name))
        rows = cursor.fetchall()

    if not rows:
        abort(404, description="No data found for the requested zip and measure_name")

    results = [dict(row) for row in rows]
    return jsonify(results)


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "endpoint": "/county_data"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
