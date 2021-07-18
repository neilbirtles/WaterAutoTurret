from .yaw_motor import yaw_motor as yaw_motor_class
from .pitch_motor import pitch_motor as pitch_motor_class
from .DRV8806_driver import DRV8806_Driver
import spidev as spidev
import wiringpi

spi_interface = spidev.SpiDev()
spi_interface.open(1, 0)
spi_interface.max_speed_hz = 500000
spi_interface.bits_per_word = 8
spi_interface.loop = False
spi_interface.mode = 3

wiringpi.wiringPiSetup()
GPIO = wiringpi.GPIO()

#setup the yaw (rotation) motor
yaw_motor = yaw_motor_class(spi_interface, GPIO)
yaw_motor.home(1000, 51200, 10)
#setup the pitch (elvation) motor
pitch_motor = pitch_motor_class(spi_interface, GPIO)
pitch_motor.home(500, 51200, 10)



