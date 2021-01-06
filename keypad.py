#!/usr/bin/env python3

import logging
import platform
import subprocess
import sys
import aiy.assistant.auth_helpers
from aiy.assistant.library import Assistant
import aiy.audio
import aiy.voicehat
from google.assistant.library.event import EventType
#import aiy.voicehat
import os, random
import aiy.device._cds as CDS

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)

import RPi.GPIO as GPIO
from time import sleep
import aiy.device._led as LED
import aiy.device._keypad as KEY
import GPIO_EX
import threading
import aiy.device._adc as ADC
import spidev
import aiy.device._buzzer as BUZZ
# import aiy.device._led as LED
# device/led.py
#sys.path.insert(0,'./device')
#import led
import aiy.device._textlcd as TLCD 
# from time import sleep
# import aiy.device._adc as ADC
import aiy.device._fan as FAN
import aiy.device._dht11 as DHT

lcd = TLCD.LCD.Adafruit_CharLCD(TLCD.LCD_RS, TLCD.LCD_E, TLCD.LCD_D4, TLCD.LCD_D5, TLCD.LCD_D6, TLCD.LCD_D7, TLCD.lcd_columns, TLCD.lcd_rows)
gasVal = 0
cdsVal = 0
temperature = 0

isBuzzer = False
isLed = False
isOk = False
isOk2 = False
isGood = False
def reset():
    global t
    global t1

    t = threading.Thread(target=KEY.threadReadKeypad, args=())
    t.daemon = True
    t.start()
    GPIO.setmode(GPIO.BCM)
    KEY.initKeypad()
    ADC.initMcp3208()
    LED.initLed(LED.LED_1)
    TLCD.initTextlcd()
    FAN.initFan(FAN.FAN_PIN1, FAN.FAN_PIN2)
    # temperature = DHT.readTemp()    

def lcd_set(text, line,line1) :
    
    lcd.set_cursor(line1, line)
    lcd.message(text)

def lcd_clear():
    # print('lcd')
    
    lcd.clear()

def shbar():
    # print('cdsVal')
    # print("hellow")
    global cdsVal
    cdsVal=ADC.readSensor(ADC.CDS_CHANNEL)

def shbar1():
    # print('gasVal')
    # print("hellow")
    global gasVal
    gasVal = ADC.readSensor(ADC.GAS_CHANNEL)

def fBuzzer():
    # print('fBuzzer')
    global isGood
    global j
    if isGood == True:
        LED.controlLed(LED.LED_1, LED.ON)
        BUZZ.playBuzzer(BUZZ.melodyList, BUZZ.noteDurations)

def ftemp():
    # print('ftemp')
    global temperature
    temperature = DHT.readTemp()
    # global cdsVal
    # shbar()

def juyeonFunction():
    global isOk
    global isGood
    global j
    j = threading.Thread(target=fBuzzer, args=())
    j.daemon = True
    j.start()

    if isOk == True:
        # print("asd")

        if cdsVal < 2000:
            lcd_clear()
            lcd_set('stop&wait',0 ,0)
            isGood = True
        
        elif 3000 > cdsVal >= 2000:
            lcd_clear()
            lcd_set('slowly',0,0)
            LED.controlLed(LED.LED_1, LED.OFF)
            isGood = True

        else:
            lcd_clear()
            lcd_set('Go',0,0)
            LED.controlLed(LED.LED_1, LED.OFF)
            isGood = False

def First():
    # print('First')
    global temperature
    global isOk2
    global gasVal
    # global gasVal 
    if isOk2 == True:
        # lcd.clear()
        print(gasVal)
        lcd_set('temp:'+str(temperature),1,0)
        sleep(1)
        if gasVal > 500 or temperature >= 26:
            FAN.controlFan(FAN.ON)
        else:
            FAN.controlFan(FAN.OFF)
            threading.Timer(10,FAN.controlFan).stop()

def tester() :
    # global temperature
    # global cdsVal
    # global gasVal
    global isOk
    global isOk2
    a = False
    # b = False
    
    # j = threading.Thread(target=juyeonFunction(), args=())
    # j.daemon = True
    # j.start()

    # j1 = threading.Thread(target=First(), args=())
    # j1.daemon = True
    # j1.start()
    lcd.clear()

    while(True):
        print("Yes, I'm listening...")
        speech = input()
        if speech == 'start':
            print('input key : ')
            while True:
                if KEY.keyData == 2 or a == True:
                    # print("text")
                    shbar()
                    shbar1()
                    ftemp()
                    isOk = True
                    isOk2 = True
                    a = True
                    juyeonFunction()
                    global j
                    x = threading.Thread(target=First, args=())
                    x.daemon = True
                    x.start()
                    sleep(1) 
                KEY.keyData = -1
            
def process_event(assistant, event):
    global t
    status_ui = aiy.voicehat.get_status_ui()
#    print("status_ui : %s"%status_ui)
    # if event.type == EventType.ON_START_FINISHED:
    #     status_ui.status('ready')
    #     if sys.stdout.isatty():
    #         print('Say "OK, Google" then speak, or press Ctrl+C to quit...')

    # elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
    #     status_ui.status('listening')
    #     print("Yes, I'm listening...")

    # elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
    #     print('You said:', event.args['text'])
    #     text = event.args['text'].lower()
    #     if text == 'ready keypad':
    #         assistant.stop_conversation()
    #         aiy.audio.say('ready keypad')
    #         t = threading.Thread(target=KEY.threadReadKeypad, args=( ))
    #         t.daemon = True
    #         t.start()

    # elif event.type == EventType.ON_END_OF_UTTERANCE:
    #     status_ui.status('thinking')

    # elif (event.type == EventType.ON_CONVERSATION_TURN_FINISHED
    #       or event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT
    #       or event.type == EventType.ON_NO_RESPONSE):
    #     status_ui.status('ready')

    # elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
    #     sys.exit(1)

def main():
    if platform.machine() == 'armv6l':          # Returns the machine type, e.g. 'i386'.
        print('Cannot run hotword demo on Pi Zero!')
        exit(-1)
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    reset()

    tester()

if __name__ == '__main__':
    # tester()
    main()