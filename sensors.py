import math
import socket
import time
from struct import unpack_from

import serial
from serial import tools
from serial.tools import list_ports


class Sensors():
    __interval = 0

    mode = "serial"
    sock = None
    ser = None

    def __init__(self, **kwargs):
        self.mode = "net" if kwargs['net'] else "serial"
        if self.mode == "net":
            print("Receiver IP: ", socket.gethostbyname(socket.gethostname()))
            udp_port = kwargs['net']
            # UDP_PORT = int(raw_input ("Enter Port "))
            print("Port: ", udp_port)
            self.sock = socket.socket(socket.AF_INET,  # Internet
                                      socket.SOCK_DGRAM)  # UDP
            self.sock.bind(("0.0.0.0", udp_port))
        else:
            port = kwargs['serial']
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

                return {'x': ax, 'y': ay, 'z': az}
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
            return {'x': ax, 'y': ay, 'z': az}

    def close(self):
        # self.file.close()
        pass

    def quaternion_to_euler_angle(self, w, x, y, z):
        t_0 = +2.0 * (w * x + y * z)
        t_1 = +1.0 - 2.0 * (x * x + y * y)
        x = math.degrees(math.atan2(t_0, t_1))

        t_2 = +2.0 * (w * y - z * x)
        t_2 = +1.0 if t_2 > +1.0 else t_2
        t_2 = -1.0 if t_2 < -1.0 else t_2
        y = math.degrees(math.asin(t_2))

        t_3 = +2.0 * (w * z + x * y)
        t_4 = +1.0 - 2.0 * (y * y + z * z)
        z = math.degrees(math.atan2(t_3, t_4))

        return (x, y, z)
