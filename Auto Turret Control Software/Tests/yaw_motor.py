from TMC5160_driver import TMC5160_driver

# TMC5160 BOB Constants
# 0.075R sense resistor give 3.1A max
MAX_I_FROM_SENSE_R = 3.1
#yaw motor uses pin 6 for chip select
YAW_MOTOR_CS = 6

class yaw_motor(TMC5160_driver):

    def __init__(self, SPI_interface, GPIO):
        super().__init__(SPI_interface, GPIO, YAW_MOTOR_CS, MAX_I_FROM_SENSE_R)
        #self.__motor_driver = TMC5160_driver(SPI_interface, GPIO,6, MAX_I_FROM_SENSE_R )
        
        #set the global current scale  first - set for 2A
        self.GSCALE = 2
        #set the currents up
        self.hold_current = 16
        self.run_current = 20
        self.hold_current_delay = 5

        # MULTISTEP_FILT = 1, EN_PWM_MODE = 1 enables stealthChop
        self.GCONF = 0x0C
        self.CHOPCONF = 0x4000005
        # [11]en_softstop = 0 (hard), [10] sg_stop = 0, [9] en_latch_encoder = 0, [8] latch_r_inactive = 0 
        # [7] latch_r_active = 0, [6] latch_l_inactive = 0, [5] latch_l_active = 0, [4] swap_lr = 0
        # [3] pol_stop_r = 1 (active low), [2] pol_stop_l = 1 (active low), [1] stop_r_enable = 0, [0] stop_l_enable = 0
        self.SWMODE = 0x0C
        self.TPWMTHRS = 0xFA

        self.SHORT_CONF = 0x1060C

        self.VSTART = 1
        self.A1 = 100
        self.V1 = 2500 #2500
        self.AMAX = 50 #25 #50
        self.VMAX = 10000 #10000
        self.DMAX = 70
        self.D1 = 100
        self.VSTOP = 100

        self.XACTUAL = 0
        self.XTARGET = 0
        self.RAMPMODE = 0
