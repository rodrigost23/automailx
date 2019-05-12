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
    parser.add_argument('-d', '--duration', type=int, nargs='?',
                        default=None, help="Duration to record in seconds")
    parser.add_argument('-a', '--activities', type=int, nargs='?',
                        default=1, help="Number of activities to record")
    args = parser.parse_args()
    filename = args.file
    duration = args.duration
    activities = args.activities

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
    print("Press Ctrl+C to terminate.")

    i = 0
    while i < activities:

        print("\n ACTIVITY %d:" % (i + 1))
        start_time = None
        total_time = None
        record_time = 0
        reply = None
        dq = deque()

        while duration is None or start_time is None or total_time <= duration:
            try:
                data = s.read()
                if data is None:
                    continue
                elif start_time is None:
                    start_time = time.time()
                    record_time = start_time - 0.5

                total_time = time.time() - start_time

                print("\r[%ds] " % (total_time), end='')
                print(str(data) + " " * 10, end='')

                if time.time() - record_time >= 0.5:
                    record_time = time.time()
                    dq.append({'time': total_time, 'data': sensors.SensorData(*data.data())})
                if dq and total_time - dq[0]['time'] >= 1: # if time more than 1 second
                    save_data = data - dq.popleft()['data']
                    with open(filename, "a", newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([i] + list(save_data.data()))
                    print("    Saved %s      " % (save_data), end='')
            except KeyboardInterrupt:
                print()
                reply = input("\n\n(C)ontinue, (q)uit, or next (a)ctivity?" + " " * 100)
                if reply in ('a', 'A', 'q', 'Q'):
                    break
                else:
                    start_time = time.time()
                    dq.clear()
                    continue

        print("\r[%ds] " % (total_time), end='')
        if reply in ('q', 'Q'):
            break

        i += 1
        if not i >= activities and not (reply == "a" or reply == "A"):
            input("Press ENTER to continue")


if __name__ == "__main__":
    main()
