import socket
from struct import unpack_from

import serial


class Sensors():
    mode = "serial"
    sock = None
    ser = None

    def __init__(self, mode):
        self.mode = mode
        if self.mode == "net":
            print("Receiver IP: ", socket.gethostbyname(socket.gethostname()))
            UDP_PORT = 5000
            # UDP_PORT = int(raw_input ("Enter Port "))
            print("Port: ", UDP_PORT)
            self.sock = socket.socket(socket.AF_INET,  # Internet
                                      socket.SOCK_DGRAM)  # UDP
            self.sock.bind(("0.0.0.0", UDP_PORT))
        else:
            self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

    def read(self):
        if self.mode == "net":
            return self.__readsocket()
        else:
            return self.__readserial()

    def __readsocket(self):
        global yaw_offset, accel
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

                return (ax, ay, az)
        except Exception as e:
            pass

    def __readserial(self):
        ax = ay = az = 0.0

        # request data by sending a character
        self.ser.write(b'r')
        # while not line_done:
        line = self.ser.readline()
        if len(line) >= 4:
            print(line)

        if line[:3] == b'ypr':
            angles = line.split(b'\t')[1:]
            if len(angles) == 3:
                ax = float(angles[0])
                ay = float(angles[1])
                az = float(angles[2].replace(b'\r\n', b''))
                print(ax, ay, az)
                return (ax, ay, az)

    def close(self):
        # self.file.close()
        pass
