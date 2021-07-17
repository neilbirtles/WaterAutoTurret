from time import sleep

#Debug printing flag
DEBUG = False

# SPI CONSTANTS
OUTPUT = 1
OUTPUT_LOW = 0
OUTPUT_HIGH = 1

#TMC5160 Registers - pulled from TMC5160 datasheet - https://www.trinamic.com/fileadmin/assets/Products/ICs_Documents/TMC5160A_Datasheet_Rev1.15.pdf 
#General Configuration Registers
GCONF       = 0x00
GSTAT       = 0x01
IFCNT       = 0x02
SLAVECONF   = 0x03
INP_OUT     = 0x04
X_COMPARE   = 0x05
OTP_PROG    = 0x06
OTP_READ    = 0x07
FACT_CONF   = 0x08
SHORT_CONF  = 0x09
DRV_CONF    = 0x0A
GSCALE      = 0x0B
OFFSET_READ = 0x0C
#Velocity Dependent Driver Feature Control Register Set
IHOLD_IRUN  = 0x10
TPOWERDOWN  = 0x11
TSTEP       = 0x12
TPWMTHRS    = 0x13
TCOOLTHRS   = 0x14
THIGH       = 0x15
#Ramp Generator Motion Control Register Set
RAMPMODE    = 0x20
XACTUAL     = 0x21
VACTUAL     = 0x22
VSTART      = 0x23
A1          = 0x24
V1          = 0x25
AMAX        = 0x26
VMAX        = 0x27
DMAX        = 0x28
D1          = 0x2A
VSTOP       = 0x2B
TZEROWAIT   = 0x2C
XTARGET     = 0x2D
#Ramp Generator Driver Feature Control Register Set
VDCMIN      = 0x33
SWMODE      = 0x34
RAMPSTAT    = 0x35
XLATCH      = 0x36
#Encoder Registers
ENCMODE     = 0x38
X_ENC        = 0x39
ENC_CONST   = 0x3A
ENC_STATUS  = 0x3B
ENC_LATCH   = 0x3C
ENC_DEVI    = 0x3D
#Motor Driver Registers
MSLUT0      = 0x60
MSLUT1      = 0x61
MSLUT2      = 0x62
MSLUT3      = 0x63
MSLUT4      = 0x64
MSLUT5      = 0x65
MSLUT6      = 0x66
MSLUT7      = 0x67
MSLUTSEL    = 0x68
MSLUTSTART  = 0x69
MSCNT       = 0x6A
MSCURACT    = 0x6B
CHOPCONF    = 0x6C
COOLCONF    = 0x6D
DCCTRL      = 0x6E
DRV_STATUS  = 0x6F
PWMCONF     = 0x70
PWM_SCALE   = 0x71
PWM_AUTO    = 0x72
LOST_STEPS  = 0x73

class TMC5160_driver:

    def __init__(self, SPI_interface, GPIO, chip_select_pin, sense_res_max_i):
        #The SPI interface to use for communicating with the device - must be compatible with SPIDEV
        self.__interface = SPI_interface
        #The chip select pin this driver will use to select the right chip
        self.__chip_select_pin = chip_select_pin
        self.__GPIO = GPIO
        #Make sure teh CS pin is set as an output
        self.__GPIO.pinMode(self.__chip_select_pin, OUTPUT)
        #Set the CS line high to disable comms with the chip
        self.__GPIO.digitalWrite(self.__chip_select_pin, OUTPUT_HIGH)
        #The sense resistor defines the max current - used in other calcs - e.g. global scaler
        self.__sense_res_max_i = sense_res_max_i

        #The TMC5160 sends status back with every transmission, stored here
        self.__latest_SPI_status = 0 #TMC5160_SPI_Status()
        #Flag used to store the success or not of the last write
        self.__last_write_success = True
        
        #Shadow registers for write only TMC5160 registers
        self.__global_scaler = 0
        self.__ihold = 0
        self.__irun = 0
        self.__ihold_delay = 0
        self.__short_conf = 0 # needs to be set to power on defaults
        #default ramp values to give a slow movement 
        self.__VSTART = 1
        self.__A1 = 100
        self.__V1 = 250 
        self.__AMAX = 25
        self.__VMAX = 1000
        self.__DMAX = 70
        self.__D1 = 100
        self.__VSTOP = 100
        
        #tracks the homing status
        self.__homed = False
        self.__max_left_steps = 0
        self.__max_right_steps = 0
    
    def __read_from_TMC5160(self, address):
        #transfers are always 40bits, MSB first
        #39-32 address bits, 31-0 data bits
        #bit 39 indicates direction - 0 for read and 1 for write - for read AND with 0x7F
        #read from the device by sending dummy data, then the requested data is returned 
        # on the next device read, so read twice as not using sequential register reads
        read_data = [address & 0x7F, 0, 0, 0, 0]
        read_buffer = self.__send_data(read_data)
        read_buffer = self.__send_data(read_data)
        
        #first byte is status info, so save it
        self.__latest_SPI_status = read_buffer[0]

        #return the 32bit word response
        return self.__extract_data_from_response(read_buffer)
    
    def __write_to_TMC5160(self, address, data):
        #transfers are always 40bits, MSB first
        #39-32 address bits, 31-0 data bits
        #bit 39 indicates direction - 0 for read and 1 for write - for write OR with 0x80
        #setup a write buffer as need to send in bytes, and put the modified addres in byte 0
        write_buffer = [address | 0x80, 0, 0, 0, 0]
        #split and move the data into the right byte positions
        #byte 0 still AND with 0xFF to remove any extra data above bit 31
        write_buffer[1] = 0xFF & (data >> 24)
        write_buffer[2] = 0xFF & (data >> 16)
        write_buffer[3] = 0xFF & (data >> 8)
        write_buffer[4] = 0xFF & data
        
        if DEBUG:
            print("Address: " +hex(address))
            print("Address OR'ed: " + hex(address | 0x80))
            print("Data: " + hex(data))
            print("Write Buffer pre send: ", end='')# + str(write_buffer))
            print('[{}]'.format(', '.join(hex(x) for x in write_buffer)))

        #write the data to the chip
        self.__send_data(write_buffer)
        #sleep(0.01)
        #perform a read (any reg works) to get the previously written info back. Using GCONF
        sent_dat = self.__send_data([0, 0, 0, 0, 0])
        check_data = self.__twos_compliment(self.__extract_data_from_response(sent_dat))

        if DEBUG:
            print("Rx Sent Data: ", end='')# + str(sent_dat))
            print('[{}]'.format(', '.join(hex(x) for x in sent_dat)))
            print("Check Data: " + hex(check_data))
        
        if check_data == data:
            #if there is match to the sent data then
            self.__last_write_success = True
        else:
            #if there is a mismatch then
            self.__last_write_success = False
            print("bad write")
            if DEBUG:
                print("bad write")
                print("data: " +hex(data))
                print("check data: " + hex(check_data))
                print("----------------------")
        
        #sleep(0.01)

    def __send_data(self, data):
        #Transfer data over the SPI bus - read and write are the same at this point
        #Select this chip and signal start of transmission by pulling CS low
        self.__GPIO.digitalWrite(self.__chip_select_pin, OUTPUT_LOW)
        #sleep(0.01)
        #Send the data
        response = self.__interface.xfer2(data)
        #Deselect this chip and signal end of transmission by pulling CS high
        #sleep(0.01)
        self.__GPIO.digitalWrite(self.__chip_select_pin, OUTPUT_HIGH)
        return response
    
    def __extract_data_from_response(self, response):
        #data is transferred MSB first in bytes so repack into 32 bit word
            
        returned_data = response[1]
        returned_data = returned_data << 8 
        returned_data |= response[2]
        returned_data = returned_data << 8 
        returned_data |= response[3]
        returned_data = returned_data << 8 
        returned_data |= response[4]
        return returned_data
    
    def __twos_compliment(self, value):
        #32 bits in all responses from the TMC5160 so use 32 bit shifts
        #check if the sign bit is set
        if (value & (1 << (32 - 1))) != 0:
            #if it is then calculate the negative value
            value = value - (1 << 32)
        #otherwise return value as is
        return value
    
    def turn_off_driver(self):
        old_chop_conf_state = self.__read_from_TMC5160(CHOPCONF)
        #set TOFF [3..0] to 0 to disable driver, so mask off bottom nibble
        self.__write_to_TMC5160(CHOPCONF, old_chop_conf_state & 0xFFFFFFF0)

    def go_to_position(self, position):
        self.set_position_mode()
        self.__write_to_TMC5160(XTARGET, position)

    def home(self, max_velocity, limit_switch_seek_distance, steps_from_switch_at_max):
        # Homing from datasheet rev 1.15 section 12.4
        #switch to the requsted VMAX for homing
        original_vmax = self.VMAX
        self.VMAX = max_velocity

        # make sure left limit switch isnt pressed, if it is move away from it - positive direction moves away from switch
        if self.at_left_limit_sw:
            print("at left limit switch")
            while self.at_left_limit_sw:
                #move away a bit
                self.go_to_position(self.current_position + 50)
                #wait for the move to finish
                while not self.position_reached:
                    sleep(0.001)
            print("moved from left limit sw")

        # dont enable motor soft stop
        self.soft_stop_enabled = False
        # activate position latching for left switch 
        self.latch_position_on_left_sw_active = True
        # activate autostop on left switch being hit
        self.stop_on_left_sw_active = True
        # move to left limit switch and get the position
        self.go_to_position(-1 * limit_switch_seek_distance)
        print("Going to left limit...")
        # As soon as the switch is hit, the position becomes latched and the motor is stopped. Wait until
        # the motor is in standstill again by polling the actual velocity VACTUAL
        if DEBUG: print("Target Pos: " + str(self.XTARGET))
        while not self.at_left_limit_sw:
            if DEBUG: 
                "Print moving to limit sw..."
                print("Latched Pos: " + str(self.latched_position))
                print("Current Pos: " + str(self.current_position))
            sleep(0.1)

        while self.current_velocity != 0:
            if DEBUG: print("waiting for zero velocity")
            sleep(0.1)
        
        if DEBUG: 
            print("Latched Pos: " + str(self.latched_position))
            print("Current Pos: " + str(self.current_position))

        self.__max_left_steps = self.latched_position

        # deactivate position latching for left switch
        self.latch_position_on_left_sw_active = False
        # deactivate autostop on left switch being hit
        self.stop_on_left_sw_active = False
        
        # Should never be at the right limit switch as have just moved to the left one but in case, make sure not on it
        if self.at_right_limit_sw:
            print("at right limit switch")
            while self.at_right_limit_sw:
                #move away a bit
                self.go_to_position(self.current_position - 50)
                #wait for the move to finish
                while not self.position_reached:
                    sleep(0.001)
            print("moved from right limit sw")

        # Activate position latching for right switch 
        self.latch_position_on_right_sw_active = True
        # activate autostop on right switch being hit
        self.stop_on_right_sw_active = True
        # move to right limit switch and get the position
        self.go_to_position(limit_switch_seek_distance)
        print("Going to right limit...")
        # As soon as the switch is hit, the position becomes latched and the motor is stopped. Wait until
        # the motor is in standstill again by polling the actual velocity VACTUAL
        if DEBUG: print("Target Pos: " + str(self.XTARGET))
        while not self.at_right_limit_sw:
            if DEBUG: 
                "Print moving to limit sw..."
                print("Latched Pos: " + str(self.latched_position))
                print("Current Pos: " + str(self.current_position))
            sleep(0.1)

        while self.current_velocity != 0:
            if DEBUG: print("waiting for zero velocity")
            sleep(0.1)
        
        if DEBUG: 
            print("Latched Pos: " + str(self.latched_position))
            print("Current Pos: " + str(self.current_position))

        self.__max_right_steps = self.latched_position

        # deactivate position latching for right switch
        self.latch_position_on_right_sw_active = False
        # deactivate autostop on right switch being hit
        self.stop_on_right_sw_active = False

        # calculate the total step range and split evenly between the left and right, for odd numbers
        #add the spare step to the right hand side
        if DEBUG: 
            print("Max Left Steps: " + str(self.__max_left_steps))
            print("Max Right Steps: " + str(self.__max_right_steps))
        total_range = (-1 * self.__max_left_steps) + self.__max_right_steps
        if DEBUG: print("Total Range: " + str(total_range))
        self.__max_left_steps = -1 * int(total_range/2) + steps_from_switch_at_max
        self.__max_right_steps = int(total_range/2) + total_range % 2 - steps_from_switch_at_max
        print("Max Left Steps: " + str(self.__max_left_steps))
        print("Max Right Steps: " + str(self.__max_right_steps))

        #set a zero at the right hand switch point
        self.set_hold_mode()
        self.XACTUAL = 0
        self.XTARGET = 0
        
        #go to the newly calculated midpoint
        print("Going to new midpoint...")
        self.go_to_position(-1 * self.__max_right_steps)
        
        while not self.position_reached:
            if DEBUG: print("Going to midpoint...")
            sleep(0.1)

        # switch to hold mode and make this the new zero
        self.set_hold_mode()
        self.XACTUAL = 0
        self.XTARGET = 0
        if DEBUG: 
            print("XACTUAL: " + str(self.XACTUAL))
            print("XTARGET: " + str(self.XTARGET))

        # disable motor soft stop
        self.soft_stop_enabled = False
        #put VMAX back to what it was before homing
        self.VMAX = original_vmax
        # set homing complete 
        self.__homed = True

        return

    @property
    def homed(self):
        return self.__homed
    
    @property
    def max_left_steps(self):
        if self.__homed:
            return self.__max_left_steps
        else:
            return 0
    
    @property
    def max_right_steps(self):
        if self.__homed:
            return self.__max_right_steps
        else:
            return 0

    @property
    def at_left_limit_sw(self):
        #left swtich status is at bit 0, 1 indicates active
        return 0x01 == (self.__read_from_TMC5160(RAMPSTAT) & 0x01)

    @property
    def at_right_limit_sw(self):
        #left swtich status is at bit 1, 1 indicates active
        return 0x02 == (self.__read_from_TMC5160(RAMPSTAT) & 0x02)

    @property
    def last_write_successful(self):
        return self.__last_write_success

    @property
    def current_SPI_status(self):
        return self.__latest_SPI_status

    @property
    def current_position(self):
        return self.__twos_compliment(self.__read_from_TMC5160(XACTUAL))
    
    @property
    def current_velocity(self):
        return self.__twos_compliment(self.__read_from_TMC5160(VACTUAL))

    @property
    def latched_position(self):
        return self.__twos_compliment(self.__read_from_TMC5160(XLATCH))

    def set_position_mode(self):
        self.__write_to_TMC5160(RAMPMODE, 0)

    def set_velocity_left_mode(self):
        self.__write_to_TMC5160(RAMPMODE, 1)
    
    def set_velocity_right_mode(self):
        self.__write_to_TMC5160(RAMPMODE, 2)
    
    def set_hold_mode(self):
        self.__write_to_TMC5160(RAMPMODE, 3)
    
    @property
    def GCONF(self):
        return self.__read_from_TMC5160(GCONF)
    
    @GCONF.setter
    def GCONF(self, value):
        self.__write_to_TMC5160(GCONF, value)

    @property
    def GSTAT(self):
        return self.__read_from_TMC5160(GSTAT)

    @GSTAT.setter
    def GSTAT(self, value):
        self.__write_to_TMC5160(GSTAT, value)

    @property
    def IOIN(self):
        return self.__read_from_TMC5160(INP_OUT)

    @property
    def OTP_READ(self):
        return self.__read_from_TMC5160(OTP_READ)

    @property
    def FACTORY_CONF(self):
        return self.__read_from_TMC5160(FACT_CONF)

    @property
    def SHORT_CONF(self):
        return self.__short_conf
    
    @SHORT_CONF.setter
    def SHORT_CONF(self, value):
        return self.__write_to_TMC5160(SHORT_CONF,value)

    @property
    def GSCALE(self):
        return self.__global_scaler

    @GSCALE.setter
    def GSCALE(self, motor_max_i):
        # Current scale value = (motor max / sense resistor max) * 256. 
        # int() truncates to 0 and want to be at upper end so add 1
        gscale_val = int((motor_max_i/self.__sense_res_max_i) * 256) + 1
        # Must be in the range 32..255 or 0, where 0 is max and 32/256..255/256 of max current
        if gscale_val <= 31: 
            gscale_val = 32
        elif gscale_val > 255:
            gscale_val = 0
        self.__write_to_TMC5160(GSCALE, gscale_val)
        if self.last_write_successful:
            #save the new gscale value if it write sucessfully
            self.__global_scaler = gscale_val            
    
    @property
    def OFFSET_READ(self):
        read_data = self.__read_from_TMC5160(OFFSET_READ)
        offset_response = [0, 0]
        #offset A is in bits 15..8
        offset_response[0] = self.__twos_compliment((read_data >> 8) & 0xFF)
        #offset B is in bits 7..0
        offset_response[1] = self.__twos_compliment(read_data & 0xFF)
        return offset_response

    @property
    def hold_current(self):
        return self.__ihold
    
    @hold_current.setter
    def hold_current(self, value):
        if value > 31 or value < 0:
            value = 0
        #ihold delay is in bits 19..16
        ihol_irun_reg_value = self.__ihold_delay << 16
        #irun is in bits 12..8
        ihol_irun_reg_value = ihol_irun_reg_value | (self.__irun << 8)
        #ihold is in bits 4..0
        ihol_irun_reg_value = ihol_irun_reg_value | value
        #write it to the chip
        self.__write_to_TMC5160(IHOLD_IRUN, ihol_irun_reg_value)
        if self.__last_write_success:
            self.__ihold = value
    
    @property
    def run_current(self):
        return self.__ihold
    
    @run_current.setter
    def run_current(self, value):
        if value > 31 or value < 0:
            value = 0
        #ihold delay is in bits 19..16
        ihol_irun_reg_value = self.__ihold_delay << 16
        #irun is in bits 12..8
        ihol_irun_reg_value = ihol_irun_reg_value | (value << 8)
        #ihold is in bits 4..0
        ihol_irun_reg_value = ihol_irun_reg_value | self.__ihold
        #write it to the chip
        self.__write_to_TMC5160(IHOLD_IRUN, ihol_irun_reg_value)
        if self.__last_write_success:
            self.__irun = value
    
    @property
    def hold_current_delay(self):
        return self.__ihold
    
    @hold_current_delay.setter
    def hold_current_delay(self, value):
        if value > 15 or value < 0:
            value = 0
        #ihold delay is in bits 19..16
        ihol_irun_reg_value = value << 16
        #irun is in bits 12..8
        ihol_irun_reg_value = ihol_irun_reg_value | (self.__irun << 8)
        #ihold is in bits 4..0
        ihol_irun_reg_value = ihol_irun_reg_value | self.__ihold
        #write it to the chip
        self.__write_to_TMC5160(IHOLD_IRUN, ihol_irun_reg_value)
        if self.__last_write_success:
            self.__ihold_delay = value
    
    @property
    def CHOPCONF(self):
        return self.__read_from_TMC5160(CHOPCONF)
    
    @CHOPCONF.setter
    def CHOPCONF(self, value):
        self.__write_to_TMC5160(CHOPCONF, value)

    @property
    def LOST_STEPS(self):
        return self.__read_from_TMC5160(LOST_STEPS)

    @property
    def DRV_STATUS(self):
        return self.__read_from_TMC5160(DRV_STATUS)
    
    @property
    def SWMODE(self):
        return self.__read_from_TMC5160(SWMODE)
    
    @SWMODE.setter
    def SWMODE(self, value):
        self.__write_to_TMC5160(SWMODE, value)

    #switch mode individual bit settings
        # [11]en_softstop = 0 (hard), [10] sg_stop = 0, [9] en_latch_encoder = 0, [8] latch_r_inactive = 0 
        # [7] latch_r_active = 0, [6] latch_l_inactive = 0, [5] latch_l_active = 0, [4] swap_lr = 0
        # [3] pol_stop_r = 1 (active low), [2] pol_stop_l = 1 (active low), [1] stop_r_enable = 0, [0] stop_l_enable = 0
    @property
    def soft_stop_enabled(self) -> bool:
        #softstop is bit 11 so mask and check for it
        return 0x800 == (self.__read_from_TMC5160(SWMODE) & 0x800)
    
    @soft_stop_enabled.setter
    def soft_stop_enabled(self, value : bool):
        if value:
            #set bit 11 to enable soft stop
            self.__write_to_TMC5160(SWMODE, self.__read_from_TMC5160(SWMODE) | 0x800)
        else:
            #clear bit 11 to disable soft stop, 11 bits used in register
            self.__write_to_TMC5160(SWMODE, self.__read_from_TMC5160(SWMODE) & 0x7FF)
    
    @property
    def latch_position_on_left_sw_active(self) -> bool:
        #latch_l_active is bit 5
        return 0x20 == (self.__read_from_TMC5160(SWMODE) & 0x20)
    
    @latch_position_on_left_sw_active.setter
    def latch_position_on_left_sw_active(self, value : bool):
        if value:
            #set bit 5 to enable
            self.__write_to_TMC5160(SWMODE, self.__read_from_TMC5160(SWMODE) | 0x20)
        else:
            #clear bit 5 to disable , 11 bits used in register
            self.__write_to_TMC5160(SWMODE, self.__read_from_TMC5160(SWMODE) & 0xFDF)
    
    @property
    def latch_position_on_right_sw_active(self) -> bool:
        #latch_r_active is bit 7
        return 0x80 == (self.__read_from_TMC5160(SWMODE) & 0x80)
    
    @latch_position_on_right_sw_active.setter
    def latch_position_on_right_sw_active(self, value : bool):
        if value:
            #set bit 7 to enable
            self.__write_to_TMC5160(SWMODE, self.__read_from_TMC5160(SWMODE) | 0x80)
        else:
            #clear bit 7 to disable, 11 bits used in register
            self.__write_to_TMC5160(SWMODE, self.__read_from_TMC5160(SWMODE) & 0xF7F)
    
    @property
    def stop_on_left_sw_active(self) -> bool:
        #stop_l_enable is bit 0
        return 0x01 == (self.__read_from_TMC5160(SWMODE) & 0x01)
    
    @stop_on_left_sw_active.setter
    def stop_on_left_sw_active(self, value : bool):
        if value:
            #set bit 0 to enable
            self.__write_to_TMC5160(SWMODE, self.__read_from_TMC5160(SWMODE) | 0x01)
        else:
            #clear bit 0 to disable , 11 bits used in register
            self.__write_to_TMC5160(SWMODE, self.__read_from_TMC5160(SWMODE) & 0xFFE)
    
    @property
    def stop_on_right_sw_active(self) -> bool:
        #stop_r_enable is bit 1
        return 0x02 == (self.__read_from_TMC5160(SWMODE) & 0x02)
    
    @stop_on_right_sw_active.setter
    def stop_on_right_sw_active(self, value : bool):
        if value:
            #set bit 1 to enable
            self.__write_to_TMC5160(SWMODE, self.__read_from_TMC5160(SWMODE) | 0x02)
        else:
            #clear bit 1 to disable , 11 bits used in register
            self.__write_to_TMC5160(SWMODE, self.__read_from_TMC5160(SWMODE) & 0xFFD)
    
    @property
    def swap_left_and_right_ref_switch(self) -> bool:
        #stop_r_enable is bit 4
        return 0x10 == (self.__read_from_TMC5160(SWMODE) & 0x10)
    
    @swap_left_and_right_ref_switch.setter
    def swap_left_and_right_ref_switch(self, value : bool):
        if value:
            #set bit 4 to enable
            self.__write_to_TMC5160(SWMODE, self.__read_from_TMC5160(SWMODE) | 0x10)
        else:
            #clear bit 4 to disable , 11 bits used in register
            self.__write_to_TMC5160(SWMODE, self.__read_from_TMC5160(SWMODE) & 0xFEF)

    @property
    def TPWMTHRS(self):
        return
    
    @TPWMTHRS.setter
    def TPWMTHRS(self, value):
        self.__write_to_TMC5160(TPWMTHRS, value)

    @property
    def RAMPMODE(self):
        return self.__read_from_TMC5160(RAMPMODE)
    
    @RAMPMODE.setter
    def RAMPMODE(self, value):
        self.__write_to_TMC5160(RAMPMODE, value)

    @property
    def XACTUAL(self) -> int:
        return self.__twos_compliment(self.__read_from_TMC5160(XACTUAL))
    
    @XACTUAL.setter
    def XACTUAL(self, value:int):
        self.__write_to_TMC5160(XACTUAL, value)
    
    @property
    def VACTUAL(self) -> int:
        return self.__twos_compliment(self.__read_from_TMC5160(VACTUAL))

    @property
    def VSTART(self):
        return self.__VSTART
    
    @VSTART.setter
    def VSTART(self, value):
        self.__write_to_TMC5160(VSTART, value)
    
    @property
    def A1(self):
        return self.__A1
    
    @A1.setter
    def A1(self, value):
        self.__write_to_TMC5160(A1, value)
    
    @property
    def V1(self):
        return self.__V1
    
    @V1.setter
    def V1(self, value):
        self.__write_to_TMC5160(V1, value)
    
    @property
    def AMAX(self):
        return self.__AMAX
    
    @AMAX.setter
    def AMAX(self, value):
        self.__write_to_TMC5160(AMAX, value)
    
    @property
    def VMAX(self):
        return self.__VMAX
    
    @VMAX.setter
    def VMAX(self, value):
        self.__write_to_TMC5160(VMAX, value)
    
    @property
    def DMAX(self):
        return self.__DMAX
    
    @DMAX.setter
    def DMAX(self, value):
        self.__write_to_TMC5160(DMAX, value)
    
    @property
    def D1(self):
        return self.__D1
    
    @D1.setter
    def D1(self, value):
        self.__write_to_TMC5160(D1, value)
    
    @property
    def VSTOP(self):
        return self.__VSTOP
    
    @VSTOP.setter
    def VSTOP(self, value):
        self.__write_to_TMC5160(VSTOP, value)
    
    @property
    def XTARGET(self) -> int:
        return self.__twos_compliment(self.__read_from_TMC5160(XTARGET))
    
    @XTARGET.setter
    def XTARGET(self, value:int):
        self.__write_to_TMC5160(XTARGET, value)
    
    @property
    def RAMPSTAT(self):
        return self.__read_from_TMC5160(RAMPSTAT)

    def curr_test(self):
        self.__write_to_TMC5160(IHOLD_IRUN, 0x1F10)
    
    @property
    def position_reached(self):
        # **** using RAMPSTAT doesnt seem to give reliable results, using compare XACTUAL and XTARGET instead
        # ramp_stat = self.__read_from_TMC5160(RAMPSTAT)
        
        # # print("RAMPSTAT: "+bin(ramp_stat))
        
        # # #position reached is bit 9 in rampstat
        # # return (ramp_stat & 0x200) == 0x200
        
        # #use event bit for position reached (bit 7) as it is less transitory
        # if (ramp_stat & 0x80) == 0x80:
        #     #position reached interrupt flag is set, clear it by writing a 1 and return true
        #     self.__write_to_TMC5160(RAMPSTAT,0x80)
        #     ramp_stat = self.__read_from_TMC5160(RAMPSTAT)
        
        #     # print("cleared RAMPSTAT: "+bin(ramp_stat))
        if self.XTARGET == self.XACTUAL:
            return True
        else:
            return False
            

