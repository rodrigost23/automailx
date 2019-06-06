#!/usr/bin/env python3
"""Reads data from the serial port and writes them to a file.
"""
import argparse
import csv
import errno
import os
import time
from collections import deque

import sensors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', default=None,
                        help="Name of the file to save")
    args = parser.parse_args()
    filename = args.file

    if filename is None:
        i = 1
        while os.path.exists("data/data%d.csv" % i):
            i += 1
        filename = "data/data%d.csv" % i

    # Create directory if it doesn't exist
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    # Start reading from serial port
    s = sensors.Sensors()
    activity = 0

    print("Waiting for signal...")
    while s.read() is None:
        pass
    print("")

    while True:
        prev_activity = activity
        activity = input("Select activity to record or Q to finish [current: %d]: " % activity)\
            or activity

        if activity in ('q', 'Q'):
            break
        try:
            activity = int(activity)
        except ValueError:
            print("Invalid option.")
            activity = prev_activity
            continue

        print("\n ACTIVITY %d:" % (activity))

        data = None
        while data is None:
            data = s.read()

        save_data = sensors.SensorData(*data.data())
        with open(filename, "a", newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([activity] + list(save_data.data()))
        print("    Saved %s      " % (save_data), end='\n\n')
    print("Finished.")


if __name__ == "__main__":
    main()
