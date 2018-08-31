#!/usr/bin/env python

import os
import socket
import subprocess
import sys
import time
from struct import *

import pygame
import serial
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

mode = "serial"
accel = tuple([0, 0, 0])
vel = tuple([0, 0, 0])
pos = tuple([0, 0.0, -7.0])
yaw_offset = 0
ax = ay = az = 0.0
yaw_mode = False


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


def draw():
    global rquad
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    glTranslatef(*pos)

    osd_text = "pitch: " + str("{0:.2f}".format(ay)) + \
        ", roll: " + str("{0:.2f}".format(ax))

    if yaw_mode:
        osd_line = osd_text + ", yaw: " + str("{0:.2f}".format(az))
    else:
        osd_line = osd_text

    drawText((-2, -2, 2), osd_line)

    # the way I'm holding the IMU board, X and Y axis are switched
    # with respect to the OpenGL coordinate system
    if yaw_mode:                             # experimental
        glRotatef(az, 0.0, 1.0, 0.0)  # Yaw,   rotate around y-axis
    else:
        glRotatef(0.0, 0.0, 1.0, 0.0)
    glRotatef(ay, 1.0, 0.0, 0.0)        # Pitch, rotate around x-axis
    glRotatef(ax, 0.0, 0.0, 1.0)     # Roll,  rotate around z-axis

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


def read_data_socket(sock):
    global ax, ay, az, yaw_offset, accel, vel, pos
    # ax = ay = az = 0.0

    try:
        data, _ = sock.recvfrom(1024)  # buffer size is 1024 bytes
        # print("received message: ", "%1.4f"
        #       % unpack_from('!f', data, 0), "%1.4f"
        #       % unpack_from('!f', data, 4), "%1.4f"
        #       % unpack_from('!f', data, 8), "%1.4f"

        #       % unpack_from('!f', data, 12), "%1.4f"
        #       % unpack_from('!f', data, 16), "%1.4f"
        #       % unpack_from('!f', data, 20), "%1.4f"

        #       % unpack_from('!f', data, 24), "%1.4f"
        #       % unpack_from('!f', data, 28), "%1.4f"
        #       % unpack_from('!f', data, 32), "%1.4f"

        #       % unpack_from('!f', data, 36), "%1.4f"
        #       % unpack_from('!f', data, 40), "%1.4f"
        #       % unpack_from('!f', data, 44), "%1.4f"

        #       % unpack_from('!f', data, 48), "%1.4f"
        #       % unpack_from('!f', data, 52), "%1.4f"
        #       % unpack_from('!f', data, 56), "%1.4f"
        #       % unpack_from('!f', data, 60), "%1.4f"
        #       % unpack_from('!f', data, 64), "%1.4f"
        #       % unpack_from('!f', data, 68), "%1.4f"
        #       % unpack_from('!f', data, 72), "%1.4f"
        #       % unpack_from('!f', data, 76), "%1.4f"
        #       % unpack_from('!f', data, 80), "%1.4f"
        #       % unpack_from('!f', data, 84), "%1.4f"
        #       % unpack_from('!f', data, 88), "%1.4f"
        #       % unpack_from('!f', data, 92))

        accel = (unpack_from('!f', data, 0)[0],
                 unpack_from('!f', data, 4)[0],
                 unpack_from('!f', data, 8)[0])

        # angles = [float(x) for x in line.split(b',')]
        angles = (unpack_from('!f', data, 36)[0],
                  unpack_from('!f', data, 40)[0],
                  unpack_from('!f', data, 44)[0])

        if len(angles) == 3:

            if yaw_offset == 0:
                yaw_offset = float(angles[0])

            # print("angles", angles)
            ax = -float(angles[2])
            ay = -float(angles[1])
            az = float(angles[0])
    except Exception as e:
        print(e)


def read_data_serial(ser):
    global ax, ay, az
    ax = ay = az = 0.0
    line_done = 0

    # request data by sending a dot
    ser.write(".")
    # while not line_done:
    line = ser.readline()
    angles = line.split(", ")
    if len(angles) == 3:
        ax = float(angles[0])
        ay = float(angles[1])
        az = float(angles[2])
        line_done = 1


def main():
    global yaw_mode, mode

    if len(sys.argv) > 1:
        if sys.argv[1] == "net":
            mode = "net"
        elif sys.argv[1] == "serial":
            mode = "serial"

    if mode == "net":
        #UDP_IP = "96.49.100.238"
        #UDP_IP = "127.0.0.1"
        UDP_IP = socket.gethostbyname(socket.gethostname())
        print("Receiver IP: ", UDP_IP)
        UDP_PORT = 5000
        # UDP_PORT = int(raw_input ("Enter Port "))
        print("Port: ", UDP_PORT)
        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.bind((UDP_IP, UDP_PORT))
    else:
        ser = serial.Serial('/dev/tty.usbserial', 38400, timeout=1)

    video_flags = OPENGL | DOUBLEBUF

    pygame.init()
    screen = pygame.display.set_mode((640, 480), video_flags)
    pygame.display.set_caption("Press Esc to quit, z toggles yaw mode")
    resize2((640, 480))
    init()
    frames = 0
    ticks = pygame.time.get_ticks()
    while True:
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break
        if event.type == KEYDOWN and event.key == K_z:
            yaw_mode = not yaw_mode
            # ser.write("z")
        if mode == "net":
            read_data_socket(sock)
        else:
            read_data_serial(ser)
        draw()

        pygame.display.flip()
        frames = frames+1

    print("fps:  %d" % ((frames*1000)/(pygame.time.get_ticks()-ticks)))
    file.close()


if __name__ == '__main__':
    main()
