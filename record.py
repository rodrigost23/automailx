import argparse
import csv
import errno
import os

import sensors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', default="data/data.csv")
    args = parser.parse_args()
    filename = args.file

    # Create directory if it doesn't exist
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    # Start reading from serial port
    s = sensors.Sensors()
    print("Press Ctrl+C to terminate.\n")
    while True:
        try:
            data = s.read()
            if data is None:
                continue
            print(str(data) + " " * 10, end='\r')
            with open(filename, "a", newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(data)

        except KeyboardInterrupt:
            print("Interrupted." + " " * 36)
            break


if __name__ == "__main__":
    main()
