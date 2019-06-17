"""Reads sensor data and deals with them
"""
import math
import socket
import time
from struct import unpack_from

import serial
from pyquaternion import Quaternion
from serial import tools
from serial.serialutil import SerialException
from serial.tools import list_ports


def quat_to_euler(*args):
    """Converts quaternion to euler angles
    """
    if len(args) == 4 and all(map(lambda x: isinstance(x, float), args)):
        w = args[0]
        x = args[1]
        y = args[2]
        z = args[3]

    elif len(args) == 1 and isinstance(args[0], Quaternion):
        w = args[0].w
        x = args[0].x
        y = args[0].y
        z = args[0].z

    else:
        raise TypeError(
            "Use either 4 floats (w, x, y, z) or one Quaternion object.")

    # roll(x-axis rotation)
    sinr_cosp = +2.0 * (w * x + y * z)
    cosr_cosp = +1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    # pitch(y-axis rotation)
    sinp = +2.0 * (w * y - z * x)
    if math.fabs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)
        # use 90 degrees if out of range
    else:
        pitch = math.asin(sinp)

    # yaw(z-axis rotation)
    siny_cosp = +2.0 * (w * z + x * y)
    cosy_cosp = +1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    pitch, yaw, roll = map(math.degrees, (pitch, roll, yaw))

    return SensorData.Triple(pitch, roll, yaw)

class SensorData():
    """Stores sensor data including orientation and angle
    """
    class Triple():
        def __init__(self, x: float, y: float, z: float):
            self.x = x
            self.y = y
            self.z = z

        def __len__(self):
            return 3

        def __getitem__(self, key):
            if key in ("x", 0):
                return self.x
            if key in ("y", 1):
                return self.y
            if key in ("z", 2):
                return self.z

            if isinstance(key, int) and key >= self.__len__():
                raise IndexError()
            else:
                raise KeyError(key)

    def __init__(self,
                 gw: float = 0.0, gx: float = 0.0, gy: float = 0.0, gz: float = 0.0,
                 ax: float = 0.0, ay: float = 0.0, az: float = 0.0,
                 angle: float = 0.0):
        self.gyro = Quaternion([gw, gx, gy, gz])
        self.accel = self.Triple(ax, ay, az)
        self.flex = angle

    @property
    def gyro_euler(self):
        """Gets Euler angles for the gyro sensor
        """
        return quat_to_euler(self.gyro.w, self.gyro.x, self.gyro.y, self.gyro.z)

    def __str__(self):
        return "gyro(%4.1f,%4.1f,%4.1f) accel(%8.1f,%8.1f,%8.1f) flex(%8.1f)" % \
            (self.gyro_euler.x, self.gyro_euler.y, self.gyro_euler.z,
             self.accel.x, self.accel.y, self.accel.z, self.flex)

    def __len__(self):
        return 8

    def __getitem__(self, key):
        if key in ("gw", 0):
            return self.gyro.w
        if key in ("gx", 1):
            return self.gyro.x
        if key in ("gy", 2):
            return self.gyro.y
        if key in ("gz", 3):
            return self.gyro.z
        if key in ("ax", 4):
            return self.gyro.x
        if key in ("ay", 5):
            return self.gyro.y
        if key in ("az", 6):
            return self.gyro.z
        if key in ("flex", 7):
            return self.flex

        if isinstance(key, int) and key >= self.__len__():
            raise IndexError()
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        if key in ("gw", 0):
            self.gyro.w = value
        if key in ("gx", 1):
            self.gyro.x = value
        if key in ("gy", 2):
            self.gyro.y = value
        if key in ("gz", 3):
            self.gyro.z = value
        if key in ("ax", 4):
            self.gyro.z = value
        if key in ("ay", 5):
            self.gyro.z = value
        if key in ("az", 6):
            self.gyro.z = value
        if key in ("flex", 7):
            self.flex = value
        else:
            raise KeyError()

    def __sub__(self, other):
        difference = SensorData(
            self.gyro.w - other.gyro.w,
            self.gyro.x - other.gyro.x,
            self.gyro.y - other.gyro.y,
            self.gyro.z - other.gyro.z,
            self.accel.x - other.accel.x,
            self.accel.y - other.accel.y,
            self.accel.z - other.accel.z,
            self.flex - other.flex
        )

        return difference

    def clf_data(self):
        """Generator of data to be used in the classifier"""
        # yield self.gyro.w
        # yield self.gyro.x
        # yield self.gyro.y
        # yield self.gyro.z
        yield self.accel.x
        yield self.accel.y
        yield self.accel.z
        yield self.flex

    def setdata(self,
                gw: float = None, gx: float = None, gy: float = None, gz: float = None,
                ax: float = None, ay: float = None, az: float = None,
                flex: float = None
                ):
        self.gyro[0] = gw or self.gyro.w
        self.gyro[1] = gx or self.gyro.x
        self.gyro[2] = gy or self.gyro.y
        self.gyro[3] = gz or self.gyro.z
        self.accel.x = ax or self.accel.x
        self.accel.y = ay or self.accel.y
        self.accel.z = az or self.accel.z
        self.flex = flex or self.flex


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
        gw = gx = gy = gz = 0.0
        ax = ay = az = 0.0
        gyro = []
        accel = []

        # request data by sending a character
        millis = int(round(time.time() * 1000))
        if (millis - self.__interval > 1000):
            # resend single character to trigger DMP init/start
            # in case the MPU is halted/reset while applet is running
            try:
                self.ser.write(b'r')
            except SerialException:
                print("\nFail to write to serial")
            __interval = millis

        # while not line_done:
        self.ser.flush()
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        line = self.ser.readline()

        # serial data is in yaw/pitch/roll format
        data = line[:-2].split(b'\t')
        if len(data) == 10 and line[:3] == b'ypr' and line[-2:] == b'\r\n':
            gyro = [0] + data[1:4] #TODO: change this workaround that uses Quaternion without w
            if data[4] == b'aworld':
                accel = data[5:8]
            if data[8] == b'flex':
                self.data.setdata(flex=float(data[9]))
        # serial data has quaternion data
        elif len(data) == 11 and line[:4] == b'quat' and line[-2:] == b'\r\n':
            gyro = data[1:5]
            if data[5] == b'aworld':
                accel = data[6:9]
            if data[9] == b'flex':
                self.data.setdata(flex=float(data[10]))

        elif len(line) > 9 and line[0:2] == b'$\x02' and line[-2:] == b'\r\n':
            q = [0.0]*4
            q[0] = ((line[2] << 8) | line[3]) / 16384.0
            q[1] = ((line[4] << 8) | line[5]) / 16384.0
            q[2] = ((line[6] << 8) | line[7]) / 16384.0
            q[3] = ((line[8] << 8) | line[9]) / 16384.0

            for i, _ in enumerate(range(4)):
                if (q[i] >= 2):
                    q[i] = -4 + q[i]
            gyro = q

        if len(gyro) == 4:
            gw = float(gyro[0])
            gx = float(gyro[1])
            gy = float(gyro[2])
            gz = float(gyro[3])
            self.data.setdata(gw=gw, gx=gx, gy=gy, gz=gz)
            if len(accel) == 3:
                ax = float(accel[0])
                ay = float(accel[1])
                az = float(accel[2])
                self.data.setdata(ax=ax, ay=ay, az=az)
            return self.data

    def close(self):
        """Not implemented. Meant to be used if file source is ever implemented.
        """
        # self.file.close()
        pass
