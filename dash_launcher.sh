#!/bin/sh
cd /home/pi/src/neuromancer_dash
/usr/bin/python3 -O neuromancer_dash.py --aidasse http://192.168.1.202:8080/sse --gpioenabled
