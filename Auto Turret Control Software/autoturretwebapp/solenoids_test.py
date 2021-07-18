from .DRV8806_driver import DRV8806_Driver
from time import sleep

#  +------+-----+----------+------+---+----+---- Model  Khadas VIM3 --+----+---+------+----------+-----+------+
#  | GPIO | wPi |   Name   | Mode | V | DS | PU/PD | Physical | PU/PD | DS | V | Mode |   Name   | wPi | GPIO |
#  +------+-----+----------+------+---+----+-------+----++----+-------+----+---+------+----------+-----+------+
#  |      |     |       5V |      |   |    |       |  1 || 21 |       |    |   |      | GND      |     |      |
#  |      |     |       5V |      |   |    |       |  2 || 22 | P/U   |    | 1 | IN   | PIN.A15  | 6   |  475 |
#  |      |     |   USB_DM |      |   |    |       |  3 || 23 | P/U   |    | 1 | IN   | PIN.A14  | 7   |  474 |
#  |      |     |   USB_DP |      |   |    |       |  4 || 24 |       |    |   |      | GND      |     |      |
#  |      |     |      GND |      |   |    |       |  5 || 25 | P/U   |    | 1 | ALT0 | PIN.AO2  | 8   |  498 |
#  |      |     |   MCU3V3 |      |   |    |       |  6 || 26 | P/U   |    | 1 | ALT0 | PIN.AO3  | 9   |  499 |
#  |      |     |  MCUNRST |      |   |    |       |  7 || 27 |       |    |   |      | 3V3      |     |      |
#  |      |     |  MCUSWIM |      |   |    |       |  8 || 28 |       |    |   |      | GND      |     |      |
#  |      |     |      GND |      |   |    |       |  9 || 29 | P/D   |    | 0 | IN   | PIN.A1   | 10  |  461 |
#  |      |  18 |     ADC0 |      |   |    |       | 10 || 30 | P/D   |    | 0 | IN   | PIN.A0   | 11  |  460 |
#  |      |     |      1V8 |      |   |    |       | 11 || 31 | P/D   |    | 0 | IN   | PIN.A3   | 12  |  463 |
#  |      |  19 |     ADC1 |      |   |    |       | 12 || 32 | P/D   |    | 0 | IN   | PIN.A2   | 13  |  462 |
#  |  506 |   1 | PIN.AO10 | ALT3 | 0 |    |   P/U | 13 || 33 | P/D   |    | 0 | IN   | PIN.A4   | 14  |  464 |
#  |      |     |     GND3 |      |   |    |       | 14 || 34 |       |    |   |      | GND      |     |      |
#  |  433 |   2 |   PIN.H6 |  OUT | 1 |    |   P/D | 15 || 35 | P/D   |    | 0 | ALT2 | PWM-F    | 15  |  432 |
#  |  434 |   3 |   PIN.H7 | ALT2 | 0 |    |   P/D | 16 || 36 |       |    |   |      | RTC      |     |      |
#  |      |     |      GND |      |   |    |       | 17 || 37 | P/D   |    | 0 | ALT2 | PIN.H4   | 16  |  431 |
#  |  497 |   4 |  PIN.AO1 | ALT0 | 1 |    |   P/U | 18 || 38 |       |    |   |      | MCU-FA1  |     |      |
#  |  496 |   5 |  PIN.AO0 | ALT0 | 1 |    |   P/U | 19 || 39 | P/D   |    | 0 | IN   | PIN.Z15  | 17  |  426 |
#  |      |     |      3V3 |      |   |    |       | 20 || 40 |       |    |   |      | GND      |     |      |
#  +------+-----+----------+------+---+----+-------+----++----+-------+----+---+------+----------+-----+------+


#vim3 GPIO pin 32
drv8806_latch_pin = 13
#vim3 GPIO pin 31
drv8806_sclk_pin = 12
#vim3 GPIO pin 29
drv8806_sdatain_pin = 10
#vim3 GPIO pin 33
drv8806_reset_pin = 14

#vim3 GPIO pin 22
motor_driver_1_select = 6
#vim3 GPIO pin 23
motor_driver_2_select = 7

water_ports = DRV8806_Driver(drv8806_latch_pin, drv8806_sclk_pin, drv8806_sdatain_pin, drv8806_reset_pin)
water_ports.turn_on_port(1)
sleep(0.5)
water_ports.turn_on_port(2)
sleep(0.5)
water_ports.turn_on_port(3)
sleep(0.5)
water_ports.turn_on_port(4)
sleep(0.5)

sleep(1)
water_ports.turn_off_port(1)
sleep(0.5)
water_ports.turn_off_port(2)
sleep(0.5)
water_ports.turn_off_port(3)
sleep(0.5)
water_ports.turn_off_port(4)


