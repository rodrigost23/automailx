import argparse
import csv
import errno
import os
import time

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
    print("Press Ctrl+C to terminate.\n")

    i = 0
    while i < activities:

        print(" ACTIVITY %d:" % (i + 1))
        start_time = None
        elapsed_time = None

        try:
            while duration is None or start_time is None or elapsed_time <= duration:
                data = s.read()
                if data is None:
                    continue
                elif start_time is None:
                    start_time = time.time()

                if elapsed_time is not None and start_time is not None:
                    print("[%ds] " % (elapsed_time), end='')

                print(str(data) + " " * 10, end='\r')
                with open(filename, "a", newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow([i] + list(data.data()))

                elapsed_time = time.time() - start_time
            print("[%ds] " % (elapsed_time), end='')

            i += 1
            if not i >= activities:
                input("Press ENTER to continue" + " " * 30)

        except KeyboardInterrupt:
            print("Interrupted." + " " * 36)
            break


if __name__ == "__main__":
    main()
