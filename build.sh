#!/usr/bin/env bash
set -euo pipefail
rm -f data.db
curl -L -o county_health_rankings.csv https://public.tableau.com/app/sample-data/County_Health_Rankings.csv
python3 - <<'PY'
import csv
from pathlib import Path

input_path = Path('county_health_rankings.csv')
output_path = Path('county_health_rankings_clean.csv')
with input_path.open(newline='', encoding='utf-8') as infile, output_path.open('w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = [
        'state',
        'county',
        'state_code',
        'county_code',
        'year_span',
        'measure_name',
        'measure_id',
        'numerator',
        'denominator',
        'raw_value',
        'confidence_interval_lower_bound',
        'confidence_interval_upper_bound',
        'data_release_year',
        'fipscode',
    ]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        writer.writerow({
            'state': row['State'],
            'county': row['County'],
            'state_code': row['State code'],
            'county_code': row['County code'],
            'year_span': row['Year span'],
            'measure_name': row['Measure name'],
            'measure_id': row['Measure id'],
            'numerator': row['Numerator'],
            'denominator': row['Denominator'],
            'raw_value': row['Raw value'],
            'confidence_interval_lower_bound': row['Confidence Interval Lower Bound'],
            'confidence_interval_upper_bound': row['Confidence Interval Upper Bound'],
            'data_release_year': row['Data Release Year'],
            'fipscode': row.get('fipscode', ''),
        })
output_path.replace(input_path)

input_path = Path('zip_county.csv')
output_path = Path('zip_county_clean.csv')
with input_path.open(newline='', encoding='utf-8') as infile, output_path.open('w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = [
        'zip',
        'default_state',
        'county',
        'county_state',
        'state_abbreviation',
        'county_code',
        'zip_pop',
        'zip_pop_in_county',
        'n_counties',
        'default_city',
    ]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        county_code = row['STCOUNTYFP'][-3:]
        county_code = str(int(county_code)) if county_code.isdigit() else row['STCOUNTYFP']
        writer.writerow({
            'zip': row['ZIP'],
            'default_state': row['STATE'],
            'county': row['COUNTYNAME'],
            'county_state': row['COUNTYNAME'],
            'state_abbreviation': row['STATE'],
            'county_code': county_code,
            'zip_pop': '',
            'zip_pop_in_county': '',
            'n_counties': '',
            'default_city': '',
        })
output_path.replace(input_path)
PY
python3 csv_to_sqlite.py data.db zip_county.csv
python3 csv_to_sqlite.py data.db county_health_rankings.csv
