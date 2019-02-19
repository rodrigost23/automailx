#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from struct import *

import pygame
from pygame.locals import *

from sensors import SensorData, Sensors
from simulation import Simulation


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
        sensors = Sensors(net=args.net, serial=args.serial)

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
                sensor_data.angle = max(
                    0.0, min(90.0, sensor_data.angle - 5))
            elif keys[pygame.K_LEFT]:
                sensor_data.angle = max(
                    0.0, min(90.0, sensor_data.angle + 5))
            elif args.demo:
                if event.type == KEYDOWN and event.key == K_UP:
                    sim.nextPose()
                elif event.type == KEYDOWN and event.key == K_DOWN:
                    sim.prevPose()

        if sensor_data is not None:
            sim.sensor_data = sensor_data
        sim.draw()

        pygame.display.flip()

        if (pygame.time.get_ticks()-ticks) >= 250:
            fps = ((frames*1000)//(pygame.time.get_ticks()-ticks))
            ticks = pygame.time.get_ticks()
            frames = 0
        pygame.display.set_caption(title + " | FPS: %d" % fps)

        frames = frames+1

    print("fps:  %d" % fps)
    if not args.demo:
        sensors.close()


if __name__ == '__main__':
    main()
