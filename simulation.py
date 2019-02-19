import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

from sensors import SensorData


class Simulation():

    sensor_data = SensorData(0.0, 0.0, 0.0)
    offset = SensorData(0.0, 0.0, 0.0)
    pose = 0
    __num_poses = 2

    def resize(self, width, height):
        if height == 0:
            height = 1
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1.0*width/height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def __init__(self, width, height):
        self.resize(width, height)
        glShadeModel(GL_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

        self.quad = gluNewQuadric()
        gluQuadricDrawStyle(self.quad, GL_LINE)
        gluQuadricTexture(self.quad, GL_TRUE)

    def nextPose(self):
        self.setPose((self.pose + 1) % self.__num_poses)

    def prevPose(self):
        self.setPose((self.pose - 1) % self.__num_poses)

    def setPose(self, pose):
        print("set pose %d" % pose)
        self.pose = pose

    def drawText(self, position, textString):
        font = pygame.font.SysFont("Courier", 18, True)
        text_surface = font.render(
            textString, True, (255, 255, 255, 255), (0, 0, 0, 255))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        glRasterPos3d(*position)
        glDrawPixels(text_surface.get_width(), text_surface.get_height(),
                     GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    def draw(self):
        sensor_data = self.sensor_data - self.offset

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        glTranslatef(0, 0.0, -7.0)

        osd_line = "pitch: " + str("{0:.2f}".format(sensor_data['y'])) + \
            ", roll: " + str("{0:.2f}".format(sensor_data['x'])) + \
            ", yaw: " + str("{0:.2f}".format(sensor_data['z']))

        self.drawText((-2, 1.9, 2), osd_line)
        # drawText((2.45, 1.9, 2), "FPS: %d" % fps)

        glTranslatef(0, 2.0, 0.0)
        # Yaw,   rotate around y-axis
        glRotatef(sensor_data['z'], 0.0, 1.0, 0.0)
        # Pitch, rotate around x-axis
        glRotatef(sensor_data['y'], 1.0, 0.0, 0.0)
        # Roll,  rotate around z-axis
        glRotatef(sensor_data['x'], 0.0, 0.0, 1.0)

        glColor3f(1, 0, 1)
        gluDisk(self.quad, 0, 0.2, 10, 1)

        glColor3f(0, 0, 1)
        gluCylinder(self.quad, 0.2, 0.15, 2, 10, 1)

        glTranslatef(0, 0, 2)

        # Flex sensor:
        # Pitch, rotate around x-axis
        glRotatef(self.sensor_data.angle, 1.0, 0.0, 0.0)

        glColor3f(0, 1, 0)
        gluDisk(self.quad, 0, 0.15, 10, 1)
        gluSphere(self.quad, 0.2, 6, 6)

        glColor3f(0.2, 0.4, 1)
        gluCylinder(self.quad, 0.15, 0.125, 1.8, 9, 1)

        glTranslatef(0, 0, 1.8)
        glColor3f(0, 1, 0)
        gluDisk(self.quad, 0, 0.125, 9, 1)

        # First part of foot

        if self.pose == 0:
            pass
        elif self.pose == 1:
            glRotatef(60.0, 1.0, 0.0, 0.0)

        glColor3f(0, 1, 0)
        gluDisk(self.quad, 0, 0.15, 10, 1)
        gluSphere(self.quad, 0.2, 6, 6)

        glBegin(GL_QUADS)

        glColor3f(1.0, 1.0, 0.0)  # Yellow
        glVertex3f(-0.2, -0.1, 0.0)
        glVertex3f(0.2, -0.1, 0.0)
        glVertex3f(0.2, -0.1, 0.3)
        glVertex3f(-0.2, -0.1, 0.3)

        glColor3f(1.0, 0.5, 0.0)  # Orange
        glVertex3f(-0.2, -0.1, 0.3)
        glVertex3f(-0.2, 0.8, 0.3)
        glVertex3f(-0.2, 0.8, 0.1)
        glVertex3f(-0.2, -0.1, 0.0)

        glColor3f(1.0, 0.5, 0.0)  # Orange
        glVertex3f(0.2, -0.1, 0.3)
        glVertex3f(0.2, 0.8, 0.3)
        glVertex3f(0.2, 0.8, 0.1)
        glVertex3f(0.2, -0.1, 0.0)

        glColor3f(1.0, 0.0, 1.0)  # Magenta
        glVertex3f(-0.2, -0.1, 0.0)
        glVertex3f(-0.2, 0.8, 0.1)
        glVertex3f(0.2, 0.8, 0.1)
        glVertex3f(0.2, -0.1, 0.0)

        glColor3f(0.0, 0.0, 1.0)  # Blue
        glVertex3f(-0.2, -0.1, 0.3)
        glVertex3f(-0.2, 0.8, 0.3)
        glVertex3f(0.2, 0.8, 0.3)
        glVertex3f(0.2, -0.1, 0.3)

        glColor3f(1.0, 0.0, 0.0)  # Red
        glVertex3f(-0.2, 0.8, 0.3)
        glVertex3f(-0.2, 0.8, 0.1)
        glVertex3f(0.2, 0.8, 0.1)
        glVertex3f(0.2, 0.8, 0.3)

        glEnd()
        glTranslatef(0, 0.8, 0.1)

        # Second part of foot

        if self.pose == 0:
            pass
        elif self.pose == 1:
            glRotatef(-60.0, 1.0, 0.0, 0.0)

        glColor3f(0, 1, 0)
        gluSphere(self.quad, 0.1, 6, 6)

        glBegin(GL_QUADS)

        glColor3f(1.0, 1.0, 0.0)  # Yellow
        glVertex3f(-0.2, 0.02, 0.0)
        glVertex3f(0.2, 0.02, 0.0)
        glVertex3f(0.2, 0.02, 0.2)
        glVertex3f(-0.2, 0.02, 0.2)

        glColor3f(1.0, 0.5, 0.0)  # Orange
        glVertex3f(-0.2, 0.02, 0.2)
        glVertex3f(-0.2, 0.4, 0.2)
        glVertex3f(-0.2, 0.4, 0.1)
        glVertex3f(-0.2, 0.02, 0.0)

        glColor3f(1.0, 0.5, 0.0)  # Orange
        glVertex3f(0.2, 0.02, 0.2)
        glVertex3f(0.2, 0.4, 0.2)
        glVertex3f(0.2, 0.4, 0.1)
        glVertex3f(0.2, 0.02, 0.0)

        glColor3f(1.0, 0.0, 1.0)  # Magenta
        glVertex3f(-0.2, 0.02, 0.0)
        glVertex3f(-0.2, 0.4, 0.1)
        glVertex3f(0.2, 0.4, 0.1)
        glVertex3f(0.2, 0.02, 0.0)

        glColor3f(0.0, 0.0, 1.0)  # Blue
        glVertex3f(-0.2, 0.02, 0.2)
        glVertex3f(-0.2, 0.4, 0.2)
        glVertex3f(0.2, 0.4, 0.2)
        glVertex3f(0.2, 0.02, 0.2)

        glColor3f(1.0, 0.0, 0.0)  # Red
        glVertex3f(-0.2, 0.4, 0.2)
        glVertex3f(-0.2, 0.4, 0.1)
        glVertex3f(0.2, 0.4, 0.1)
        glVertex3f(0.2, 0.4, 0.2)

        glEnd()
