#!/usr/bin/env python3
import csv
import sqlite3
import sys
from pathlib import Path

def make_table_name(csv_path: Path) -> str:
    return csv_path.stem


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv
    if len(argv) != 3:
        print("Usage: python3 csv_to_sqlite.py <database.db> <data.csv>", file=sys.stderr)
        return 1

    db_path = Path(argv[1])
    csv_path = Path(argv[2])

    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}", file=sys.stderr)
        return 1

    table_name = make_table_name(csv_path)

    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        try:
            headers = next(reader)
        except StopIteration:
            print("CSV file is empty", file=sys.stderr)
            return 1

        headers = [header.strip() for header in headers]
        if not headers:
            print("CSV file has no headers", file=sys.stderr)
            return 1

        placeholders = ", ".join("?" for _ in headers)
        columns = ", ".join(headers)
        create_columns = ", ".join(f"{column} TEXT" for column in headers)

        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            cursor.execute(f"CREATE TABLE {table_name} ({create_columns})")
            insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            rows = []
            for row in reader:
                if len(row) != len(headers):
                    raise ValueError("CSV row has different number of columns than header")
                rows.append([value for value in row])

            if rows:
                cursor.executemany(insert_sql, rows)
            conn.commit()
        finally:
            conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
