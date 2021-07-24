from .DRV8806_driver import DRV8806_Driver

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

print("Setting up solenoid driver")
water_ports = DRV8806_Driver(drv8806_latch_pin, drv8806_sclk_pin, drv8806_sdatain_pin, drv8806_reset_pin)