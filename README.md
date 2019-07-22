# AutomailX

[![CircleCI](https://circleci.com/gh/rodrigost23/automailx.svg?style=shield&circle-token=67feb067e3f7a0dd1a27d8a9de1ec440112a0a93)](https://circleci.com/gh/rodrigost23/automailx)

| File                                   | Description                                        |
|----------------------------------------|----------------------------------------------------|
| [automailx.py](automailx.py)           | Reads data from serial or from UDP and shows in 3D |
| [record.py](record.py)                 | Records data from serial to a file                 |
| [automailx.ino](automailx.ino)         | Sends data via serial                              |
| [teapot/teapot.pde](teapot/teapot.pde) | Reads data from serial and shows in 3D             |

## Arduino requirements

* [i2cdevlib/Arduino/I2Cdev](https://github.com/jrowberg/i2cdevlib/tree/6dd5e46eb66539ac3be3f8f8e1b06c7b0373f3cc/Arduino/I2Cdev)
* [i2cdevlib/Arduino/MPU6050](https://github.com/jrowberg/i2cdevlib/tree/6dd5e46eb66539ac3be3f8f8e1b06c7b0373f3cc/Arduino/MPU6050)

## Python script instructions

Run `pip install -r requirements.txt` to get the dependencies.

    usage: automailx.py [-h] [--net [port] | --serial [port] | --demo]

    optional arguments:
    -h, --help       show this help message and exit
    --net [port]     Listen to sensor data over UDP
    --serial [port]  Listen to sensor data over serial (default)
    --demo           Only show 3D model with no sensor data

## Serial data format

The current configuration uses baud rate of `115200` and outputs the following format in the Arduino:

`ypr	x	y	z	aworld	x	y	z	flex	x`

Yaw/Pitch/Roll for the whole orientation, then acceleration relative to world, then the resistance of the flex sensor, each separated by a tab character.
