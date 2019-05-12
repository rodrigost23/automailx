"""Reads sensor data and deals with them
"""
import math
import socket
import time
from struct import unpack_from

import serial
from serial import tools
from serial.tools import list_ports


class SensorData():
    """Stores sensor data including orientation and angle
    """

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, angle: float = 0.0):
        self.imu = [{
            'x': x,
            'y': y,
            'z': z
        }]

        self.flex = [angle]

    @property
    def x(self):
        """Gets x for the imu sensor
        """
        return self.imu[0]["x"]

    @x.setter
    def x(self, value):
        """Sets x for the imu sensor
        """
        self.imu[0]["x"] = value

    @property
    def y(self):
        """Gets y for the imu sensor
        """
        return self.imu[0]["y"]

    @y.setter
    def y(self, value):
        """Sets y for the imu sensor
        """
        self.imu[0]["y"] = value

    @property
    def z(self):
        """Gets z for the imu sensor
        """
        return self.imu[0]["z"]

    @z.setter
    def z(self, value):
        """Sets z for the imu sensor
        """
        self.imu[0]["z"] = value

    @property
    def angle(self):
        """Gets angle for the flex sensor
        """
        return self.flex[0]

    @angle.setter
    def angle(self, value):
        """Sets angle for the flex sensor
        """
        self.flex[0] = value

    def __str__(self):
        return "imu(%.1f,%.1f,%.1f) flex(%.1f)" % (self.x, self.y, self.z, self.angle)

    def __len__(self):
        return 4

    def __getitem__(self, key):
        if key in ("x", 0):
            return self.x
        if key in ("y", 1):
            return self.y
        if key in ("z", 2):
            return self.z
        if key in ("angle", 3):
            return self.angle

        if isinstance(key, int) and key >= self.__len__():
            raise IndexError()
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        if key in ("x", 0):
            self.x = value
        if key in ("y", 1):
            self.y = value
        if key in ("z", 2):
            self.z = value
        if key in ("angle", 3):
            self.angle = value
        else:
            raise KeyError()

    def __sub__(self, other):
        difference = SensorData(
            self.x - other.x, self.y - other.y, self.z - other.z)
        difference.angle = self.angle - other.angle
        return difference

    def data(self):
        yield self.x
        yield self.y
        yield self.z
        yield self.angle

    def setdata(self, x: float = None, y: float = None, z: float = None, angle: float = None):
        self.x = x or self.x
        self.y = y or self.y
        self.z = z or self.z
        self.angle = angle or self.angle


class Sensors():
    """Reads sensor data from UDP or serial ports
    """
    __interval = 0

    mode = "serial"
    sock = None
    ser = None
    data = None

    def __init__(self, net_port=False, serial_port=True):
        """
        Keyword Arguments:
            net_port {int|bool} -- UDP port or {False} if not UDP (default: {False})
            serial_port {str|bool} -- Serial port or {False} if not serial (default: {True})
        """
        self.data = SensorData()
        self.mode = "net" if net_port else "serial"
        if self.mode == "net":
            print("Receiver IP: ", socket.gethostbyname(socket.gethostname()))
            udp_port = net_port
            # UDP_PORT = int(raw_input ("Enter Port "))
            print("Port: ", udp_port)
            self.sock = socket.socket(socket.AF_INET,  # Internet
                                      socket.SOCK_DGRAM)  # UDP
            self.sock.bind(("0.0.0.0", udp_port))
        else:
            port = serial_port
            serial.tools.list_ports.grep

            try:
                search = serial.tools.list_ports.grep(port)
                next(search)
            except Exception:
                port_list = serial.tools.list_ports.comports()
                for p in port_list:
                    if 'arduino' in p.description.lower():
                        port = p.device
                        break
                else:
                    port = port_list[-1].device

            baud_rate = 115200
            print("Serial port:", port)
            print("Baud rate:", baud_rate)
            self.ser = serial.Serial(port, baud_rate, timeout=1)

    def read(self):
        """Reads data from source defined in {mode}.
        """
        if self.mode == "net":
            return self.__readsocket()
        else:
            return self.__readserial()

    def __readsocket(self, yaw_offset=0):
        # ax = ay = az = 0.0

        try:
            data, _ = self.sock.recvfrom(1024)  # buffer size is 1024 bytes
            print("received message: ", "%1.4f"
                  % unpack_from('!f', data, 0), "%1.4f"
                  % unpack_from('!f', data, 4), "%1.4f"
                  % unpack_from('!f', data, 8), "%1.4f"

                  % unpack_from('!f', data, 12), "%1.4f"
                  % unpack_from('!f', data, 16), "%1.4f"
                  % unpack_from('!f', data, 20), "%1.4f"

                  % unpack_from('!f', data, 24), "%1.4f"
                  % unpack_from('!f', data, 28), "%1.4f"
                  % unpack_from('!f', data, 32), "%1.4f"

                  % unpack_from('!f', data, 36), "%1.4f"
                  % unpack_from('!f', data, 40), "%1.4f"
                  % unpack_from('!f', data, 44), "%1.4f"

                  % unpack_from('!f', data, 48), "%1.4f"
                  % unpack_from('!f', data, 52), "%1.4f"
                  % unpack_from('!f', data, 56), "%1.4f"
                  % unpack_from('!f', data, 60), "%1.4f"
                  % unpack_from('!f', data, 64), "%1.4f"
                  % unpack_from('!f', data, 68), "%1.4f"
                  % unpack_from('!f', data, 72), "%1.4f"
                  % unpack_from('!f', data, 76), "%1.4f"
                  % unpack_from('!f', data, 80), "%1.4f"
                  % unpack_from('!f', data, 84), "%1.4f"
                  % unpack_from('!f', data, 88), "%1.4f"
                  % unpack_from('!f', data, 92))

            accel = (unpack_from('!f', data, 0),
                     unpack_from('!f', data, 4),
                     unpack_from('!f', data, 8))

            # angles = [float(x) for x in line.split(b',')]
            angles = (unpack_from('!f', data, 36)[0],
                      unpack_from('!f', data, 40)[0],
                      unpack_from('!f', data, 44)[0])

            if len(angles) == 3:

                if yaw_offset == 0:
                    yaw_offset = float(angles[0])

                print("angles", angles)
                ax = -float(angles[2])
                ay = -float(angles[1])
                az = float(angles[0])

                self.data.setdata(ax, ay, az)
                return self.data
        except Exception as e:
            pass

    def __readserial(self):
        ax = ay = az = 0.0
        angles = []

        # request data by sending a character
        millis = int(round(time.time() * 1000))
        if (millis - self.__interval > 1000):
            # resend single character to trigger DMP init/start
            # in case the MPU is halted/reset while applet is running
            self.ser.write(b'r')
            __interval = millis

        # while not line_done:
        self.ser.flush()
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        line = self.ser.readline()

        if line[:3] == b'ypr' and line[-2:] == b'\r\n':
            angles = line.split(b'\t')[1:-2]

        elif len(line) > 9 and line[0:2] == b'$\x02' and line[-2:] == b'\r\n':
            q = [0.0]*4
            q[0] = ((line[2] << 8) | line[3]) / 16384.0
            q[1] = ((line[4] << 8) | line[5]) / 16384.0
            q[2] = ((line[6] << 8) | line[7]) / 16384.0
            q[3] = ((line[8] << 8) | line[9]) / 16384.0

            for i, _ in enumerate(range(4)):
                if (q[i] >= 2):
                    q[i] = -4 + q[i]
            # TODO: Use quaternion directly
            angles = self.quaternion_to_euler_angle(*q)

        if len(angles) == 3:
            ax = float(angles[0])
            ay = float(angles[1])
            az = float(angles[2])
            # print({'x': ax, 'y': ay, 'z': az})
            self.data.setdata(ax, ay, az)
            return self.data

    def close(self):
        """Not implemented. Meant to be used if file source is ever implemented.
        """
        # self.file.close()
        pass

    def quaternion_to_euler_angle(self, w, x, y, z):
        """Converts quaternion to euler angles
        """
        t_0 = +2.0 * (w * x + y * z)
        t_1 = +1.0 - 2.0 * (x * x + y * y)
        a_x = math.degrees(math.atan2(t_0, t_1))

        t_2 = +2.0 * (w * y - z * x)
        t_2 = +1.0 if t_2 > +1.0 else t_2
        t_2 = -1.0 if t_2 < -1.0 else t_2
        a_y = math.degrees(math.asin(t_2))

        t_3 = +2.0 * (w * z + x * y)
        t_4 = +1.0 - 2.0 * (y * y + z * z)
        a_z = math.degrees(math.atan2(t_3, t_4))

        return (a_x, a_y, a_z)
