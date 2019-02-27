# AutomailX
[![CircleCI](https://circleci.com/gh/rodrigost23/automailx.svg?style=shield)](https://circleci.com/gh/rodrigost23/automailx)

| File                             | Description                                        |
|----------------------------------|----------------------------------------------------|
| [automailx.py](automailx.py)     | Reads data from serial or from UDP and shows in 3D |
| [automailx.ino](automailx.ino)   | Sends data via serial                              |
| [automailx.pde](automailx.pde)   | Reads data from serial and shows in 3D             |

## Arduino requirements:
* [i2cdevlib/Arduino/I2Cdev](https://github.com/jrowberg/i2cdevlib/tree/6dd5e46eb66539ac3be3f8f8e1b06c7b0373f3cc/Arduino/I2Cdev)
* [i2cdevlib/Arduino/MPU6050](https://github.com/jrowberg/i2cdevlib/tree/6dd5e46eb66539ac3be3f8f8e1b06c7b0373f3cc/Arduino/MPU6050)

## Python script instructions:
Run `pip install -r requirements.txt` to get the dependencies.

    usage: automailx.py [-h] [--net [port] | --serial [port] | --demo]

    optional arguments:
    -h, --help       show this help message and exit
    --net [port]     Listen to sensor data over UDP
    --serial [port]  Listen to sensor data over serial (default)
    --demo           Only show 3D model with no sensor data
