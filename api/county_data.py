import json
import os
import re
import sqlite3
from flask import Flask, jsonify, request

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
DATABASE_PATH = os.environ.get("DATA_DB", "data.db")
app = Flask(__name__)


def get_db_connection():
    if not os.path.exists(DATABASE_PATH):
        raise FileNotFoundError(f"Database file not found: {DATABASE_PATH}")
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def validate_zip(zip_code):
    if isinstance(zip_code, int):
        zip_code = f"{zip_code:05d}"
    elif isinstance(zip_code, str):
        zip_code = zip_code.strip()
    else:
        return None
    return zip_code if ZIP_REGEX.fullmatch(zip_code) else None


@app.route("/", methods=["POST"])
@app.route("/<path:any_path>", methods=["POST"])
def county_data(any_path=None):
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400

    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Request JSON must be an object"}), 400

    if data.get("coffee") == "teapot":
        return jsonify({"error": "I'm a teapot"}), 418

    if "zip" not in data or "measure_name" not in data:
        return jsonify({"error": "Missing required fields: zip and measure_name"}), 400

    zip_code = validate_zip(data["zip"])
    if zip_code is None:
        return jsonify({"error": "zip must be a 5-digit string"}), 400

    measure_name = data["measure_name"]
    if not isinstance(measure_name, str):
        return jsonify({"error": "measure_name must be a string"}), 400
    measure_name = measure_name.strip()
    if measure_name not in ALLOWED_MEASURES:
        return jsonify({"error": "measure_name is not valid"}), 400

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
        return jsonify({"error": str(exc)}), 500

    with conn:
        cursor = conn.execute(query, (zip_code, measure_name))
        rows = cursor.fetchall()

    if not rows:
        return jsonify({"error": "No data found for the requested zip and measure_name"}), 404

    results = [dict(row) for row in rows]
    return jsonify(results), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
