#
# dht22 - pulls temperature and humidity data from a DHT22
# ========================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import Adafruit_DHT

from time import sleep

class DHT22Data:
    humidity = None
    temperature = None

    def __init__(self, humidity=0.0, temperature=0.0):
        self.humidity = humidity
        self.temperature = temperature

class DHT22:

    __dht_sensor = Adafruit_DHT.DHT22
    __dht_pin = 4

    __last_humidity = 0
    __last_temperature = 0

    # NOTE: (Adam) 2020-11-29 Pi GPIO timings mean we might not get a value off the DHT22, best effort
    #         will return the last value if the read attempt fails.
    @classmethod
    def best_effort_read(class_object, return_metric=False):
        humidity, temperature = Adafruit_DHT.read(class_object.__dht_sensor, class_object.__dht_pin)
        # Use last values unless both humidity and temperature return. I have seen some funky values
        # if only one value returns None and you still try to use the other.
        if None != humidity and None != temperature:
            class_object.__last_humidity = humidity
            class_object.__last_temperature = temperature
        else:
            #if __debug__:
                #print("DHT22 read attempt failed, falling back on previous values")

            humidity = class_object.__last_humidity
            temperature = class_object.__last_temperature

        if False == return_metric:
            temperature = (temperature * 1.8) + 32

        return humidity, temperature


    # Will block and retry up to 15 times with 2 seconds between attempts until GPIO timings align to
    # give us a value.
    @classmethod
    def read_retry(class_object, return_metric=False):
        humidity, temperature = Adafruit_DHT.read_retry(class_object.__dht_sensor, class_object.__dht_pin)
        assert(None != humidity and None != temperature)

        if False == return_metric:
            temperature = (temperature * 1.8) + 32

        return humidity, temperature

    @classmethod
    def threadable_read_retry(class_object, dht22_data_queue, return_metric = False):
        assert(None != dht22_data_queue)

        dht22_data = DHT22Data(class_object.read_retry(return_metric))
        dht22_data_queue.append(dht22_data)


def main():
    while True:
        humidity, temperature = DHT22.read_retry()
        #humidity, temperature = DHT22.best_effort_read()
        print("Humidity: {:0.1f}%   Temp: {:0.1f}F".format(humidity, temperature))
        sleep(1)

if __name__ == "__main__":
    main()
