#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from struct import *

import pygame
from pygame.locals import *

from sensors import Sensors
from simulation import Simulation


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--net', metavar='port', const=5000, default=None,
                       type=int, nargs='?', help='Listen to sensor data over UDP')
    group.add_argument('--serial', metavar='port', const=True, default=None,
                       nargs='?', help='Listen to sensor data over serial (default)')
    args = parser.parse_args()
    if not args.net and not args.serial:
        args = parser.parse_args(['--serial'])

    sensors = Sensors(net=args.net, serial=args.serial)

    video_flags = OPENGL | DOUBLEBUF

    pygame.init()
    pygame.display.set_mode((853, 480), video_flags)

    title = "Press Esc to quit"
    pygame.display.set_caption(title)
    sim = Simulation(853, 480)
    frames = 0
    fps = 0
    ticks = pygame.time.get_ticks()
    while True:
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break
        # if event.type == KEYDOWN and event.key == K_z:
        #     ser.write("z")
        angles = sensors.read()
        if angles is not None:
            sim.angles = angles
        sim.draw()

        pygame.display.flip()

        if (pygame.time.get_ticks()-ticks) >= 250:
            fps = ((frames*1000)//(pygame.time.get_ticks()-ticks))
            ticks = pygame.time.get_ticks()
            frames = 0
        pygame.display.set_caption(title + " | FPS: %d" % fps)

        frames = frames+1

    print("fps:  %d" % fps)
    sensors.close()


if __name__ == '__main__':
    main()
