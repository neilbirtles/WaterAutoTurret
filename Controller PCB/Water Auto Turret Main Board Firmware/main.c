/*
 * File:   main.c
 * Author: neilb
 * 
 */

// CONFIG
#pragma config FOSC = INTOSCIO  // Oscillator Selection bits (INTOSCIO oscillator: I/O function on RA4/OSC2/CLKOUT pin, I/O function on RA5/OSC1/CLKIN)
#pragma config WDTE = OFF        // Watchdog Timer Enable bit (WDT enabled)
#pragma config PWRTE = OFF      // Power-up Timer Enable bit (PWRT disabled)
#pragma config MCLRE = OFF       // MCLR Pin Function Select bit (MCLR pin function is MCLR)
#pragma config CP = OFF         // Code Protection bit (Program memory code protection is disabled)
#pragma config CPD = OFF        // Data Code Protection bit (Data memory code protection is disabled)
#pragma config BOREN = ON       // Brown Out Detect (BOR enabled)
#pragma config IESO = ON        // Internal External Switchover bit (Internal External Switchover mode is enabled)
#pragma config FCMEN = ON       // Fail-Safe Clock Monitor Enabled bit (Fail-Safe Clock Monitor is enabled

#include "main.h"
#include <xc.h>



//the following line needs to be added to a target program to allow the bootloader
//to detect that 
//const unsigned char app_loaded __at(0xFFF) = 0x55;

void SYSTEM_Initialize(void)
{
    PIN_MANAGER_Initialize();
    OSCILLATOR_Initialize();
    WDT_Initialize();
}

void PIN_MANAGER_Initialize(void)
{
    //CIN pins are configured as I/O, COUT pin is configured as I/O, Comparator output disabled, Comparator off
    CMCON0 = 0x07;
    //GP2, GP1 inputs, all others outputs
    TRISIO = 0x06;
    //GP2 analog input, AD conversion FOSC/64
    ANSEL = 0x64;
    //weak pull up enabled
    OPTION_REGbits.nGPPU = 0;
    //WPU1 enabled, all others disabled
    WPU = 0x02;
}

void OSCILLATOR_Initialize(void)
{
    // SCS FOSC; IRCF 500KHz; 
    OSCCON = 0x30;
    // TUN 0; 
    OSCTUNE = 0x00;
    // SBOREN disabled; 
    PCONbits.SBODEN = 0x00;
}

void WDT_Initialize(void)
{
    // WDTPS 1:65536; SWDTEN OFF; 
    WDTCON = 0x16;
}

void main(void) {
    
    int batt_voltage_ok = 1;
    int batt_charging = 0; 
    
    SYSTEM_Initialize();
    
    //Flash red LED on startup, leave on as power to VIM3 board is off at this point
    Red_LED = 0;
    __delay_ms(250);
    Red_LED = 1;
    __delay_ms(250);
    Red_LED = 0;

    //make sure that the turn on main power is off
    Turn_On_Main_Power = 0;
    //turn the main power off on startup
    Turn_Off_Main_Power = 1;
    __delay_ms(250);
    Turn_Off_Main_Power = 0;
    //let settle for 1 second
    __delay_ms(1000);
    
    //get the inverse of initial value to trigger at least one loop of power setup
    batt_charging = !Batt_Charge_Indicator;
    
    Turn_On_Main_Power = 1;
    __delay_ms(250);
    Turn_On_Main_Power = 0;
    //turn off the red LED
    Red_LED = 1;
    
    //check for battery charging and low battery voltage - if either detected
    // then turn off the power to the rest of the board and the VIM3
    while (1) {
        //measure battery voltage TODO
            //if ok then red LED off, set flag to allow power on
            //if not ok then red LED on and turn off power to main board, set flag to prevent power on
        
        //see if battery charging state has changed since last time
        if (Batt_Charge_Indicator != batt_charging){
            //debounce and check if still different
            __delay_ms(100);
            if (Batt_Charge_Indicator != batt_charging){
                //status has changed so save new status
                batt_charging = Batt_Charge_Indicator;
                //A Batt_Charge_Indicator value of 0 indicates that no charging 
                //plug is joined in.
                //If battery is not charging and lower power flag not set then 
                //turn on power to main board
                if (!batt_charging && batt_voltage_ok){
                    //latching relay so power coil, wait for it to settle, then remove power
                    Turn_On_Main_Power = 1;
                    __delay_ms(250);
                    Turn_On_Main_Power = 0;
                    //turn off the red LED
                    Red_LED = 1;
                //otherwise the battery is charging or in a low voltage state
                // so turn off power to main board
                }else{
                    //latching relay so power coil, wait for it to settle, then remove power
                    Turn_Off_Main_Power = 1;
                    __delay_ms(250);
                    Turn_Off_Main_Power = 0;
                    //turn on the red LED
                    Red_LED = 0;
                }
            }
        }
        
        //only check every half second
        __delay_ms(500);
    }
}
