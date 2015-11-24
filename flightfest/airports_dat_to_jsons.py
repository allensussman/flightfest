import csv
import json
import argparse

from constants import AIRPORT_LAT_LONG_FILE, AIRPORT_TIMEZONE_FILE


DEFAULT_AIRPORT_DAT = 'airports.dat'
HELP_TEMPLATE = '{} (default: {})'
DESCRIPTION = 'From OpenFlights\' airport.dat (http://openflights.org/data.html), create (1) a ' \
              'JSON file with major airports and their lat/longs and (2) a JSON file with ' \
              'airports and their timezone, in hours after UTC time.'


def output_lat_long_file(airport_data_file, lat_long_file):
    with open(airport_data_file) as f:
        # Don't include airports with \N for ICAO code or with 'Muni' (for municipal) in the name
        lat_longs = [{'code': row[4], 'lat': float(row[6]), 'long': float(row[7])}
                     for row in csv.reader(f) if row[4] and row[5] != '\N' and 'Muni' not in row[1]]
    output_json(lat_longs, lat_long_file)


def output_timezone_file(airport_data_file, timezone_file):
    with open(airport_data_file) as f:
        timezone_dict = {row[4]: float(row[9]) for row in csv.reader(f) if row[4] and row[9]}
    output_json(timezone_dict, timezone_file)


def output_json(dictionary, filename):
    with open(filename, 'w') as f:
        json.dump(dictionary, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--input_file", "-i", dest="input_file", default=DEFAULT_AIRPORT_DAT,
                        help=HELP_TEMPLATE.format('Input airport data file', DEFAULT_AIRPORT_DAT))
    parser.add_argument("--output_lat_long_file", "-l", dest="lat_long_file",
                        default=AIRPORT_LAT_LONG_FILE,
                        help=HELP_TEMPLATE.format('Output airport lat long file',
                                                  AIRPORT_LAT_LONG_FILE))
    parser.add_argument("--output_timezone_file", "-t", dest="timezone_file",
                        default=AIRPORT_TIMEZONE_FILE,
                        help=HELP_TEMPLATE.format('Output airport timezone file',
                                                  AIRPORT_TIMEZONE_FILE))

    args = parser.parse_args()

    output_lat_long_file(args.input_file, args.lat_long_file)
    output_timezone_file(args.input_file, args.timezone_file)
