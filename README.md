# Neuromancer Dash
Provides standalone monitoring of computer health data using AIDA64 LCD data streams. Neuromancer Dash supports multiple pages and can also pull data from other hardware such as temperature and humidity sensors.

Inspired by JayzTwoCents' external monitor panel: https://www.youtube.com/watch?v=RTdniu3gn3Y

# Hardware
Neuromancer Dash will run on anything with an external display that's capable of running pygame 2.0.0. For my dashboard I'm using a Raspberry Pi Zero W and 5" 480x320 HDMI LCD panel.

# Host Installation
Install AIDA64 (required, I used AIDA64 Extreme)
Install RivaTunerStatisticsServer (optional if you want FPS data)

1. Open AIDA64 Extreme
2. File -> Preferences
3. Hardware Monitoring -> LCD -> Remote Sensor -> Enabled RemoteSensor LCD support
4. Hardware Monitoring -> LCD -> LCD Items -> Import, choose file in assets\aida64_layouts
5. Hardware Monitoring -> Update Frequency -> Change LCD to 100ms (or whatever you're comfortable with)
6. Open the port configured by AIDA64's RemoteSensor support in your firewall (default 8080)

# Raspberry Pi Client Installation
1. Clone this repository onto your client

2. Install Python 3 components:
    * pip3 install sseclient
    * pip3 install pygame --upgrade
    * pip3 install Adafruit_DHT

3. Install required SDL2 components:
    * sudo apt-get install libsdl2-ttf-2.0-0 libsdl2-mixer-2.0-0 libsdl2-image-2.0-0

4. Update dash_launcher.sh with the IP and port number for your Host machine

# Execution
Two options:
1. Run **dash_launcher.sh**, this can be added to your crontab for automatic startup
2. Run **python3 neuromancerdash.py --aidasse http://example_ip:8080/sse**
