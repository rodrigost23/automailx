#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)


def drawText(position, textString):
    font = pygame.font.SysFont("Courier", 18, True)
    textSurface = font.render(
        textString, True, (255, 255, 255, 255), (0, 0, 0, 255))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glRasterPos3d(*position)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(),
                 GL_RGBA, GL_UNSIGNED_BYTE, textData)


def draw(fps: int):
    global rquad
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    glTranslatef(0, 0.0, -7.0)

    osd_line = "pitch: " + str("{0:.2f}".format(ay)) + \
        ", roll: " + str("{0:.2f}".format(ax)) + \
        ", yaw: " + str("{0:.2f}".format(az))

    drawText((-2, -2, 2), osd_line)
    # drawText((2.45, 1.9, 2), "FPS: %d" % fps)

    # the way I'm holding the IMU board, X and Y axis are switched
    # with respect to the OpenGL coordinate system
    glRotatef(az, 0.0, 1.0, 0.0)  # Yaw,   rotate around y-axis
    glRotatef(ay, 1.0, 0.0, 0.0)  # Pitch, rotate around x-axis
    glRotatef(ax, 0.0, 0.0, 1.0)  # Roll,  rotate around z-axis

    glBegin(GL_QUADS)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(1.0, 0.2, -1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(1.0, 0.2, 1.0)

    glColor3f(1.0, 0.5, 0.0)
    glVertex3f(1.0, -0.2, 1.0)
    glVertex3f(-1.0, -0.2, 1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(1.0, -0.2, -1.0)

    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, -0.2, 1.0)
    glVertex3f(1.0, -0.2, 1.0)

    glColor3f(1.0, 1.0, 0.0)
    glVertex3f(1.0, -0.2, -1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(1.0, 0.2, -1.0)

    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(-1.0, -0.2, 1.0)

    glColor3f(1.0, 0.0, 1.0)
    glVertex3f(1.0, 0.2, -1.0)
    glVertex3f(1.0, 0.2, 1.0)
    glVertex3f(1.0, -0.2, 1.0)
    glVertex3f(1.0, -0.2, -1.0)
    glEnd()


def main(mode):
    global ax, ay, az
    sensors = Sensors(mode)

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
    main(sys.argv[1] if len(sys.argv) > 1 else "serial")
