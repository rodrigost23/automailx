#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse

import pygame
from pygame.locals import (DOUBLEBUF, K_DOWN, K_ESCAPE, K_UP, KEYDOWN, OPENGL,
                           QUIT, RESIZABLE, VIDEORESIZE, K_r)

from sensors import SensorData, Sensors
from simulation import Simulation
from clf_predict import Predict


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--net', metavar='port', const=5000, default=None,
                       type=int, nargs='?', help='Listen to sensor data over UDP')
    group.add_argument('--serial', metavar='port', const=True, default=None,
                       nargs='?', help='Listen to sensor data over serial (default)')
    group.add_argument('--demo', action='store_const', dest='demo',
                       const=True, help='Only show 3D model with no sensor data')
    args = parser.parse_args()
    if not args.net and not args.serial and not args.demo:
        args = parser.parse_args(['--serial'])

    if not args.demo:
        sensors = Sensors(net_port=args.net, serial_port=args.serial)

    video_flags = OPENGL | DOUBLEBUF | RESIZABLE

    pygame.init()
    pygame.display.set_mode((900, 500), video_flags)

    title = "AutomailX"
    pygame.display.set_caption(title)
    sim = Simulation(900, 500)
    frames = 0
    fps = 0
    ticks = pygame.time.get_ticks()
    sensor_data = SensorData()
    prediction = None
    try:
        predictor = Predict()
    except Exception as exception:
        print("Predictor failed:", exception.with_traceback)
        predictor = None
    while True:
        if not args.demo:
            sensor_data = sensors.read() or sensor_data

        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break
        # if event.type == KEYDOWN and event.key == K_z:
        #     ser.write("z")
        elif event.type == VIDEORESIZE:
            pygame.display.set_mode(event.dict['size'], video_flags)
            sim.resize(*event.dict['size'])
        elif event.type == KEYDOWN and event.key == K_r:
            sim.recenter()
        else:
            keys = pygame.key.get_pressed()  # checking pressed keys
            if keys[pygame.K_RIGHT]:
                sensor_data.flex = max(
                    0.0, min(90.0, sensor_data.flex - 5))
            elif keys[pygame.K_LEFT]:
                sensor_data.flex = max(
                    0.0, min(90.0, sensor_data.flex + 5))
            elif args.demo:
                if event.type == KEYDOWN and event.key == K_UP:
                    sim.nextPose()
                elif event.type == KEYDOWN and event.key == K_DOWN:
                    sim.prevPose()

        if sensor_data is not None:
            sim.sensor_data = sensor_data
            if not args.demo and predictor is not None:
                prediction = predictor.predict(sensor_data) or 0
                sim.setPose(prediction)
                print(" Prediction: %s   " % prediction, end='')
        sim.draw()

        pygame.display.flip()

        if (pygame.time.get_ticks()-ticks) >= 250:
            fps = ((frames*1000)//(pygame.time.get_ticks()-ticks))
            ticks = pygame.time.get_ticks()
            frames = 0
        prediction_title = ("| Prediction: %d" % prediction) if prediction is not None else ""
        pygame.display.set_caption("%s | FPS: %3d %s" % (title, fps, prediction_title))

        frames = frames+1

    if not args.demo:
        sensors.close()


if __name__ == '__main__':
    main()
