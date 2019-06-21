#!/usr/bin/env python3
"""Reads data from the serial port and writes them to a file.
"""
import argparse
import csv
import errno
import os
import time
from collections import deque

import pygame
from pygame.locals import (DOUBLEBUF, K_0, K_9, K_DOWN, K_ESCAPE, K_KP0, K_KP9,
                           K_KP_ENTER, K_RETURN, K_UP, KEYDOWN, OPENGL, QUIT,
                           RESIZABLE, VIDEORESIZE, K_q, K_r)

from sensors import SensorData, Sensors
from simulation import Simulation


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

    sensors = Sensors()

    video_flags = OPENGL | DOUBLEBUF | RESIZABLE

    pygame.init()
    pygame.display.set_mode((900, 500), video_flags)

    title = "Press Esc to quit"
    pygame.display.set_caption(title)
    sim = Simulation(900, 500)
    frames = 0
    fps = 0
    ticks = pygame.time.get_ticks()
    sensor_data = SensorData()
    activity = 0

    while True:
        sensor_data = sensors.read() or sensor_data

        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and (event.key == K_ESCAPE or event.key == K_q)):
            break

        elif event.type == VIDEORESIZE:
            pygame.display.set_mode(event.dict['size'], video_flags)
            sim.resize(*event.dict['size'])

        elif event.type == KEYDOWN and event.key == K_r:
            sim.recenter()

        elif event.type == KEYDOWN and event.key in range(K_0, K_9+1):
            activity = int(event.key - K_0)

        elif event.type == KEYDOWN and event.key in range(K_KP0, K_KP9+1):
            activity = int(event.key - K_KP0)

        elif event.type == KEYDOWN and (event.key == K_RETURN or event.key == K_KP_ENTER):
            print("\n - ACTIVITY %d:" % (activity), end='')

            save_data = list(sensor_data.clf_data())
            with open(filename, "a", newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([activity] + save_data)
            print(" Saved %s      " % save_data, end='\n\n')

        if sensor_data is not None:
            sim.sensor_data = sensor_data

        sim.draw()

        pygame.display.flip()

        if (pygame.time.get_ticks()-ticks) >= 250:
            fps = ((frames*1000)//(pygame.time.get_ticks()-ticks))
            ticks = pygame.time.get_ticks()
            frames = 0
        pygame.display.set_caption(
            title + " | FPS: %d | Activity %d" % (fps, activity))

        frames = frames+1

    sensors.close()


if __name__ == "__main__":
    main()
