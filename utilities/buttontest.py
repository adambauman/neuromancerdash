import RPi.GPIO as GPIO
from time import sleep

print ("Starting button test!")

g_buttonpin = 15
GPIO.setmode(GPIO.BCM) # USE GPIO number pin addressing
# Switch connected to 3.3v with small inline resistor
GPIO.setup(g_buttonpin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

print("Button test ready, start pressin'!")
while True:
    if GPIO.input(g_buttonpin):
        print("Button pressed!")

    sleep(0.1)
