import csv
import json
import argparse


def airports_data_to_json(input_file, output_file):
    with open(input_file) as f:
        reader = csv.reader(f)
        airports_json = [{'code': row[4], 'lat': float(row[6]), 'long': float(row[7])}
                         for row in reader if row[4] and row[5] != '\N' and 'Muni' not in row[1]]

    with open(output_file, 'w') as f:
        json.dump(airports_json, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Input Parameters')
    parser.add_argument("--input_file", "-i", dest="input_file", default="airports.dat",
                        help="Input airports data file (default: airports.dat)")
    parser.add_argument("--output_file", "-o", dest="output_file", default="airports.json",
                        help="Output airports json file (default: airports.json)")

    args = parser.parse_args()

    airports_data_to_json(args.input_file, args.output_file)