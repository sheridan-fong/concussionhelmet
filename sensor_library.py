import busio
import board
import smbus
import adafruit_bno055

class Orientation_Sensor(object):

    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.bno055 = adafruit_bno055.BNO055(self.i2c)

    def euler_angles(self):
        return self.bno055.euler

    def lin_acceleration(self):
        return self.bno055.linear_acceleration

    def accelerometer(self):
        return self.bno055.acceleration

    def gravity(self):
        return self.bno055.gravity

    def gyroscope(self):
        return self.bno055.gyro

    def temperature(self):
        return self.bno055.temperature

    def magnetic_field(self):
        return self.bno055.magnetic
