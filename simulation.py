"""Shows a 3D simulation of a leg prosthesis
"""
import copy
import math

import OpenGL.GL as gl
import OpenGL.GLU as glu
from numpy.lib import math
import pygame
from pyquaternion import Quaternion
from sensors import SensorData, quat_to_euler


def quat_to_axis_rotation(*args):
    """Converts quaternion to euler angles
    """
    if len(args) == 4 and all(map(lambda x: isinstance(x, float), args)):
        Quaternion(args).unit

    elif len(args) == 1 and isinstance(args[0], Quaternion):
        quat = args[0].unit

    else:
        raise TypeError(
            "Use either 4 floats (w, x, y, z) or one Quaternion object.")

    # 2 * math.acos(quat.w)
    angle = math.atan2(math.sqrt(sum(i**2 for i in quat.vector)), quat.w)
    # assuming quaternion normalised then w is less than 1, so term always positive.
    s = math.sqrt(1-quat.w * quat.w)
    if s < 0.001:  # test to avoid divide by zero, s is always positive due to sqrt
        # if s close to zero then direction of axis not important
        x = quat.x  # if it is important that axis is normalised then replace with x=1; y=z=0;
        y = quat.y
        z = quat.z
    else:
        x = quat.x / s  # normalise axis
        y = quat.y / s
        z = quat.z / s

    # theta = 2 * \
    #     math.atan2(math.sqrt(sum(i**2 for i in quat.vector)), quat.w)
    # x, y, z = (n / math.sin(theta / 2) for n in quat.vector) \
    #     if theta != 0 else (0, 0, 0)

    return (math.degrees(angle), z, x, -y)


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
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl.glClearDepth(1.0)

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
        #FIXME: Workaround to avoid using quaternions
        quat = Quaternion(sensor_data.gyro.w, sensor_data.gyro.x,
                          sensor_data.gyro.y, sensor_data.gyro.z)#.unit
        offset = Quaternion(self.offset.gyro.w, self.offset.gyro.x,
                            self.offset.gyro.y, self.offset.gyro.z)

        if offset:
            #TODO: Change back to quaternions
            # quat = offset.inverse * sensor_data.gyro
            quat = quat - offset
            self.flex_bent = self.offset.flex - self.flex_straight + self.flex_bent
            self.flex_straight = self.offset.flex

        gyro_euler = quat_to_euler(quat)
        rotation = quat_to_axis_rotation(quat)
        flex_angle = self.translate_range(
            self.sensor_data.flex, self.flex_straight, self.flex_bent, 0.0, 90.0)

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LEQUAL)
        gl.glHint(gl.GL_PERSPECTIVE_CORRECTION_HINT, gl.GL_NICEST)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glLoadIdentity()
        gl.glTranslatef(0, 0.0, -7.0)

        osd_line = \
            "x: {0:<7.2f}".format(quat.x) + \
            "y: {0:<7.2f}".format(quat.y) + \
            "z: {0:<7.2f}".format(quat.z) + \
            "flex: {0:>8}".format("{0:.2f}°".format(flex_angle))

        self.drawText((-2, 1.9, 2), osd_line)

        gl.glTranslatef(0, 2.0, 0.0)
        #TODO: Change back to quaternions
        # gl.glRotatef(-gyro_euler.x, 0, 1, 0)
        # gl.glRotatef(-gyro_euler.y, 1, 0, 0)
        # gl.glRotatef(gyro_euler.z*2, 0, 0, 1)
        # gl.glRotatef(quat.x, 0, 1, 0)
        gl.glRotatef(-2*quat.y, 0, 0, 1)
        gl.glRotatef(quat.z, 1, 0, 0)
        gl.glRotatef(120, .5, .5, -.5)

        gl.glColor3f(1, 0, 1)
        glu.gluDisk(self.quad, 0, 0.2, 10, 1)

        gl.glColor3f(0, 0, 1)
        glu.gluCylinder(self.quad, 0.2, 0.15, 2, 10, 1)

        gl.glTranslatef(0, 0, 2)

        # Flex sensor:
        # Pitch, rotate around x-axis
        gl.glRotatef(flex_angle, 1.0, 0.0, 0.0)

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
