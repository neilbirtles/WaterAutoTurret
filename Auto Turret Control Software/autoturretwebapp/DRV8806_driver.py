import wiringpi as GPIO
import time

OUTPUT = 1
OUTPUT_LOW = 0
OUTPUT_HIGH = 1

class DRV8806_Driver:

    def __init__(self, latch_pin, sclk_pin, sdatain_pin, reset_pin):
        self.__latch_pin = latch_pin
        self.__sclk_pin = sclk_pin
        self.__sdatain_pin = sdatain_pin
        self.__reset_pin = reset_pin

        self.__port_1_state = 0
        self.__port_2_state = 0
        self.__port_3_state = 0
        self.__port_4_state = 0

        GPIO.wiringPiSetup()
        GPIO.pinMode(self.__latch_pin, OUTPUT)
        GPIO.pinMode(self.__sclk_pin, OUTPUT)
        GPIO.pinMode(self.__sdatain_pin, OUTPUT)
        GPIO.pinMode(self.__reset_pin, OUTPUT)
        
        #do initial reset of DRV8806
        #set all the interface pins low
        GPIO.digitalWrite(self.__latch_pin, OUTPUT_LOW)
        GPIO.digitalWrite(self.__sclk_pin, OUTPUT_LOW)
        GPIO.digitalWrite(self.__sdatain_pin, OUTPUT_LOW)
        #reset DRV8806
        GPIO.digitalWrite(self.__reset_pin, OUTPUT_HIGH)
        time.sleep(0.001)
        GPIO.digitalWrite(self.__reset_pin, OUTPUT_LOW)

    def turn_on_port(self, port_id):    
        #build port output states from requested new and previous states, save new state
        if (port_id == 1):
            port_states = [ 1, self.__port_2_state, self.__port_3_state, self.__port_4_state ]
            self.__port_1_state = 1
            self.__write_to_DRV8806(port_states)
        elif (port_id == 2):
            port_states = [ self.__port_1_state, 1, self.__port_3_state, self.__port_4_state ]
            self.__port_2_state = 1
            self.__write_to_DRV8806(port_states)
        elif (port_id == 3):
            port_states = [ self.__port_1_state, self.__port_2_state, 1, self.__port_4_state ]
            self.__port_3_state = 1
            self.__write_to_DRV8806(port_states)
        elif (port_id == 4):
            port_states = [ self.__port_1_state, self.__port_2_state, self.__port_3_state, 1 ]
            self.__port_4_state = 1
            self.__write_to_DRV8806(port_states)
    
    
    def turn_on_ports(self, port_1=True, port_2=True, port_3=True, port_4=True):
        port_states = [port_1, port_2, port_3, port_4]
        self.__port_1_state = port_1
        self.__port_2_state = port_2
        self.__port_3_state = port_3
        self.__port_4_state = port_4
        self.__write_to_DRV8806(port_states)

    def turn_off_port(self, port_id):    
        #build port output states from requested new and previous states, save new state
        if (port_id == 1):
            port_states = [ 0, self.__port_2_state, self.__port_3_state, self.__port_4_state ]
            self.__port_1_state = 0
            self.__write_to_DRV8806(port_states)
        elif (port_id == 2):
            port_states = [ self.__port_1_state, 0, self.__port_3_state, self.__port_4_state ]
            self.__port_2_state = 0
            self.__write_to_DRV8806(port_states)
        elif (port_id == 3):
            port_states = [ self.__port_1_state, self.__port_2_state, 0, self.__port_4_state ]
            self.__port_3_state = 0
            self.__write_to_DRV8806(port_states)
        elif (port_id == 4):
            port_states = [ self.__port_1_state, self.__port_2_state, self.__port_3_state, 0 ]
            self.__port_4_state = 0
            self.__write_to_DRV8806(port_states)
    
    
    def turn_off_ports(self, port_1=False, port_2=False, port_3=False, port_4=False):
        port_states = [port_1, port_2, port_3, port_4]
        self.__port_1_state = port_1
        self.__port_2_state = port_2
        self.__port_3_state = port_3
        self.__port_4_state = port_4
        self.__write_to_DRV8806(port_states)

    def __write_to_DRV8806(self, port_states):
        for state in port_states:
            #write the data bit
            GPIO.digitalWrite(self.__sdatain_pin, state)
            time.sleep(0.001)
            #clock it into the DRV8806
            GPIO.digitalWrite(self.__sclk_pin, OUTPUT_HIGH)
            time.sleep(0.001)
            GPIO.digitalWrite(self.__sclk_pin, OUTPUT_LOW)
        
        #when all data clocked in then latch it into the outputs
        time.sleep(0.001)
        GPIO.digitalWrite(self.__latch_pin, OUTPUT_HIGH)
        time.sleep(0.001)
        GPIO.digitalWrite(self.__latch_pin, OUTPUT_LOW)


