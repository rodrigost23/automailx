#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import subprocess
import sys
from struct import *

import pygame
import serial
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

from sensors import Sensors

accel = tuple()
pos = tuple()
yaw_offset = 0
ax = ay = az = 0.0


def resize2(width_height):
    (width, height) = width_height

    if height == 0:
        height = 1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*width/height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def init():
    global quad
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    quad = gluNewQuadric()
    gluQuadricDrawStyle(quad, GL_LINE)
    gluQuadricTexture(quad, GL_TRUE)


def drawText(position, textString):
    font = pygame.font.SysFont("Courier", 18, True)
    textSurface = font.render(
        textString, True, (255, 255, 255, 255), (0, 0, 0, 255))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glRasterPos3d(*position)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(),
                 GL_RGBA, GL_UNSIGNED_BYTE, textData)


def draw(fps: int):
    global quad
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    glTranslatef(0, 0.0, -7.0)

    osd_line = "pitch: " + str("{0:.2f}".format(ay)) + \
        ", roll: " + str("{0:.2f}".format(ax)) + \
        ", yaw: " + str("{0:.2f}".format(az))

    drawText((-2, -2, 2), osd_line)
    # drawText((2.45, 1.9, 2), "FPS: %d" % fps)

    glTranslatef(0, 2.0, 0.0)
    glRotatef(az, 0.0, 1.0, 0.0)  # Yaw,   rotate around y-axis
    glRotatef(ay, 1.0, 0.0, 0.0)  # Pitch, rotate around x-axis
    glRotatef(ax, 0.0, 0.0, 1.0)  # Roll,  rotate around z-axis

    glColor3f(1, 0, 1)
    gluDisk(quad, 0, 0.2, 10, 1)

    glColor3f(0, 0, 1)
    gluCylinder(quad, 0.2, 0.15, 2, 10, 1)

    glTranslatef(0, 0, 2)

    glColor3f(0, 1, 0)
    gluDisk(quad, 0, 0.15, 10, 1)
    gluSphere(quad, 0.2, 6, 6)

    glColor3f(0.2, 0.4, 1)
    gluCylinder(quad, 0.15, 0.125, 1.8, 9, 1)

    glTranslatef(0, 0, 1.8)
    glColor3f(0, 1, 0)
    gluDisk(quad, 0, 0.125, 9, 1)


def main(**kwargs):
    global ax, ay, az
    sensors = Sensors(**kwargs)

    video_flags = OPENGL | DOUBLEBUF

    pygame.init()
    screen = pygame.display.set_mode((853, 480), video_flags)

    title = "Press Esc to quit"
    pygame.display.set_caption(title)
    resize2((853, 480))
    init()
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
        if angles != None:
            ax, ay, az = angles
        draw(fps)
        # print(ax,ay,az)

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
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--net', metavar='port', const=5000, default=None,
                       type=int, nargs='?', help='Listen to sensor data over UDP')
    group.add_argument('--serial', metavar='port', const='/dev/ttyACM0', default=None,
                       nargs='?', help='Listen to sensor data over serial (default)')
    args = parser.parse_args()
    if not args.net and not args.serial:
        args = parser.parse_args(['--serial'])

    main(net=args.net, serial=args.serial)
