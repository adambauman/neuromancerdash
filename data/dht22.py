#
# dht22 - pulls temperature and humidity data from a DHT22
# ========================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

from time import sleep

import Adafruit_DHT

class DHT22Data:
    humidity = None
    temperature = None

    def __init__(self, humidity=0.0, temperature=0.0):
        self.humidity = humidity
        self.temperature = temperature

class DHT22:

    _dht_sensor = Adafruit_DHT.DHT22
    _dht_pin = 4

    _last_humidity = 0
    _last_temperature = 0

    # NOTE: (Adam) 2020-11-29 Pi GPIO timings mean we might not get a value off the DHT22, best effort
    #         will return the last value if the read attempt fails.
    @classmethod
    def best_effort_read(class_object, return_metric=False):
        humidity, temperature = Adafruit_DHT.read(class_object._dht_sensor, class_object._dht_pin)
        # Use last values unless both humidity and temperature return. I have seen some funky values
        # if only one value returns None and you still try to use the other.
        if humidity is not None and temperature is not None:
            class_object._last_humidity = humidity
            class_object._last_temperature = temperature
        else:
            #if __debug__:
                #print("DHT22 read attempt failed, falling back on previous values")

            humidity = class_object._last_humidity
            temperature = class_object._last_temperature

        if not return_metric:
            temperature = (temperature * 1.8) + 32

        return DHT22Data(humidity, temperature)


    # Will block and retry up to 15 times with 2 seconds between attempts until GPIO timings align to
    # give us a value.
    @classmethod
    def read_retry(class_object, return_metric=False):
        humidity, temperature = Adafruit_DHT.read_retry(class_object._dht_sensor, class_object._dht_pin)
        assert(humidity is not None and temperature is not None)

        if False == return_metric:
            temperature = (temperature * 1.8) + 32

        return DHT22Data(humidity, temperature)

    @classmethod
    def threadable_read_retry(class_object, dht22_data_queue, return_metric = False):
        assert(dht22_data_queue is not None)

        while True:
            dht22_data = class_object.read_retry(return_metric)
            dht22_data_queue.append(dht22_data)

            # NOTE: (Adam) 2020-12-04 Ambient data is going to change slowly, we can sleep for a bit to free
            #         resources for other tasks.
            sleep(300)


def main():
    while True:
        humidity, temperature = DHT22.read_retry()
        print("Humidity: {:0.1f}%   Temp: {:0.1f}F".format(humidity, temperature))
        sleep(1)

if __name__ == "__main__":
    main()
