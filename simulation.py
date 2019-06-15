"""Shows a 3D simulation of a leg prosthesis
"""
import copy

import OpenGL.GL as gl
import OpenGL.GLU as glu
import pygame
from pyquaternion import Quaternion

from sensors import SensorData


class Simulation():
    """Shows a 3D simulation of a leg prosthesis
    """
    sensor_data = SensorData()
    offset = SensorData()
    pose = 0
    __num_poses = 2
    flex_bent = 29000.0
    flex_straight = 64000.0

    def translate_range(self, value, leftMin, leftMax, rightMin, rightMax):
        """Translates one range to another"""
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)

    def resize(self, width, height):
        if height == 0:
            height = 1
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        glu.gluPerspective(45, 1.0*width/height, 0.1, 100.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

    def __init__(self, width: int, height: int):
        """
        Arguments:
            width {int} -- Window width in pixels
            height {int} -- Window height in pixels
        """
        self.resize(width, height)
        gl.glShadeModel(gl.GL_SMOOTH)
        gl.glClearColor(0.0, 0.0, 0.0, 0.0)
        gl.glClearDepth(1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LEQUAL)
        gl.glHint(gl.GL_PERSPECTIVE_CORRECTION_HINT, gl.GL_NICEST)

        self.quad = glu.gluNewQuadric()
        glu.gluQuadricDrawStyle(self.quad, gl.GL_LINE)
        glu.gluQuadricTexture(self.quad, gl.GL_TRUE)

    def nextPose(self):
        """Show next pose of the foot
        """
        self.setPose((self.pose + 1) % self.__num_poses)

    def prevPose(self):
        """Show previous pose of the foot
        """
        self.setPose((self.pose - 1) % self.__num_poses)

    def setPose(self, pose: int):
        """Sets a specific pose

        Arguments:
            pose {int} -- The pose number
        """
        self.pose = pose

    def recenter(self, data: SensorData = None):
        """Sets an offset to define the resting standing pose

        Keyword Arguments:
            data {SensorData} -- the sensor data to set as the resting pose, or
            {None} to set the current sensor data (default: {None})
        """
        if data is None:
            data = self.sensor_data

        self.offset = copy.deepcopy(data)

    def drawText(self, position, textString):
        font = pygame.font.SysFont("Courier", 18, True)
        text_surface = font.render(
            textString, True, (255, 255, 255, 255), (0, 0, 0, 255))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        gl.glRasterPos3d(*position)
        gl.glDrawPixels(text_surface.get_width(), text_surface.get_height(),
                        gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, text_data)

    def draw(self):
        """Draws one frame in the OpenGL window
        """
        sensor_data = self.sensor_data
        print("\r%s" % sensor_data, end='')
        quat = Quaternion(sensor_data.gyro.w, sensor_data.gyro.x,
                          sensor_data.gyro.y, sensor_data.gyro.z)
        offset = Quaternion(self.offset.gyro.w, self.offset.gyro.x,
                            self.offset.gyro.y, self.offset.gyro.z)
        if offset:
            quat = quat * offset.inverse

        angle = self.translate_range(
            self.sensor_data.flex, self.flex_straight, self.flex_bent, 0.0, 90.0)

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glLoadIdentity()
        gl.glTranslatef(0, 0.0, -7.0)

        osd_line = "x: " + "{0:.2f}".format(sensor_data.gyro_euler.x) + \
            ", y: " + "{0:.2f}".format(sensor_data.gyro_euler.y) + \
            ", z: " + "{0:.2f}".format(sensor_data.gyro_euler.z) + \
            ", flex: " + "{0:.2f}°".format(angle)

        self.drawText((-2, 1.9, 2), osd_line)

        gl.glTranslatef(0, 2.0, 0.0)
        gl.glRotatef(120, .5, .5, -.5)
        gl.glRotatef(quat.degrees, -quat.x, quat.z, quat.y)

        gl.glColor3f(1, 0, 1)
        glu.gluDisk(self.quad, 0, 0.2, 10, 1)

        gl.glColor3f(0, 0, 1)
        glu.gluCylinder(self.quad, 0.2, 0.15, 2, 10, 1)

        gl.glTranslatef(0, 0, 2)

        # Flex sensor:
        # Pitch, rotate around x-axis
        gl.glRotatef(angle, 1.0, 0.0, 0.0)

        gl.glColor3f(0, 1, 0)
        glu.gluDisk(self.quad, 0, 0.15, 10, 1)
        glu.gluSphere(self.quad, 0.2, 6, 6)

        gl.glColor3f(0.2, 0.4, 1)
        glu.gluCylinder(self.quad, 0.15, 0.125, 1.8, 9, 1)

        gl.glTranslatef(0, 0, 1.8)
        gl.glColor3f(0, 1, 0)
        glu.gluDisk(self.quad, 0, 0.125, 9, 1)

        # First part of foot

        if self.pose == 0:
            pass
        elif self.pose == 1:
            gl.glRotatef(60.0, 1.0, 0.0, 0.0)

        gl.glColor3f(0, 1, 0)
        glu.gluDisk(self.quad, 0, 0.15, 10, 1)
        glu.gluSphere(self.quad, 0.2, 6, 6)

        gl.glBegin(gl.GL_QUADS)

        gl.glColor3f(1.0, 1.0, 0.0)  # Yellow
        gl.glVertex3f(-0.2, -0.1, 0.0)
        gl.glVertex3f(0.2, -0.1, 0.0)
        gl.glVertex3f(0.2, -0.1, 0.3)
        gl.glVertex3f(-0.2, -0.1, 0.3)

        gl.glColor3f(1.0, 0.5, 0.0)  # Orange
        gl.glVertex3f(-0.2, -0.1, 0.3)
        gl.glVertex3f(-0.2, 0.8, 0.3)
        gl.glVertex3f(-0.2, 0.8, 0.1)
        gl.glVertex3f(-0.2, -0.1, 0.0)

        gl.glColor3f(1.0, 0.5, 0.0)  # Orange
        gl.glVertex3f(0.2, -0.1, 0.3)
        gl.glVertex3f(0.2, 0.8, 0.3)
        gl.glVertex3f(0.2, 0.8, 0.1)
        gl.glVertex3f(0.2, -0.1, 0.0)

        gl.glColor3f(1.0, 0.0, 1.0)  # Magenta
        gl.glVertex3f(-0.2, -0.1, 0.0)
        gl.glVertex3f(-0.2, 0.8, 0.1)
        gl.glVertex3f(0.2, 0.8, 0.1)
        gl.glVertex3f(0.2, -0.1, 0.0)

        gl.glColor3f(0.0, 0.0, 1.0)  # Blue
        gl.glVertex3f(-0.2, -0.1, 0.3)
        gl.glVertex3f(-0.2, 0.8, 0.3)
        gl.glVertex3f(0.2, 0.8, 0.3)
        gl.glVertex3f(0.2, -0.1, 0.3)

        gl.glColor3f(1.0, 0.0, 0.0)  # Red
        gl.glVertex3f(-0.2, 0.8, 0.3)
        gl.glVertex3f(-0.2, 0.8, 0.1)
        gl.glVertex3f(0.2, 0.8, 0.1)
        gl.glVertex3f(0.2, 0.8, 0.3)

        gl.glEnd()
        gl.glTranslatef(0, 0.8, 0.1)

        # Second part of foot

        if self.pose == 0:
            pass
        elif self.pose == 1:
            gl.glRotatef(-60.0, 1.0, 0.0, 0.0)

        gl.glColor3f(0, 1, 0)
        glu.gluSphere(self.quad, 0.1, 6, 6)

        gl.glBegin(gl.GL_QUADS)

        gl.glColor3f(1.0, 1.0, 0.0)  # Yellow
        gl.glVertex3f(-0.2, 0.02, 0.0)
        gl.glVertex3f(0.2, 0.02, 0.0)
        gl.glVertex3f(0.2, 0.02, 0.2)
        gl.glVertex3f(-0.2, 0.02, 0.2)

        gl.glColor3f(1.0, 0.5, 0.0)  # Orange
        gl.glVertex3f(-0.2, 0.02, 0.2)
        gl.glVertex3f(-0.2, 0.4, 0.2)
        gl.glVertex3f(-0.2, 0.4, 0.1)
        gl.glVertex3f(-0.2, 0.02, 0.0)

        gl.glColor3f(1.0, 0.5, 0.0)  # Orange
        gl.glVertex3f(0.2, 0.02, 0.2)
        gl.glVertex3f(0.2, 0.4, 0.2)
        gl.glVertex3f(0.2, 0.4, 0.1)
        gl.glVertex3f(0.2, 0.02, 0.0)

        gl.glColor3f(1.0, 0.0, 1.0)  # Magenta
        gl.glVertex3f(-0.2, 0.02, 0.0)
        gl.glVertex3f(-0.2, 0.4, 0.1)
        gl.glVertex3f(0.2, 0.4, 0.1)
        gl.glVertex3f(0.2, 0.02, 0.0)

        gl.glColor3f(0.0, 0.0, 1.0)  # Blue
        gl.glVertex3f(-0.2, 0.02, 0.2)
        gl.glVertex3f(-0.2, 0.4, 0.2)
        gl.glVertex3f(0.2, 0.4, 0.2)
        gl.glVertex3f(0.2, 0.02, 0.2)

        gl.glColor3f(1.0, 0.0, 0.0)  # Red
        gl.glVertex3f(-0.2, 0.4, 0.2)
        gl.glVertex3f(-0.2, 0.4, 0.1)
        gl.glVertex3f(0.2, 0.4, 0.1)
        gl.glVertex3f(0.2, 0.4, 0.2)

        gl.glEnd()
