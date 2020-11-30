#
# dht22 - pulls temperature and humidity data from a DHT22
# ========================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import Adafruit_DHT

class DHT22:
    def __init__(self, return_metric=False):
        self.__return_metric = return_metric
        self.__dht_sensor = Adafruit_DHT.DHT22
        self.__dht_pin = 4

    @classmethod
    def read(class_object):
        humidity, temperature = Adafruit_DHT.read_retry(self.__dht_sensor, self.__dht_pin)
        if None != temperature:
            temperature = (temperature * 1.8) + 32

        return humidity, temperature


def main(argv):
    while True:
        print("Humidity={2:0.1f}%     Temp={0:0.1f}F".format(DHT22.read())

if __name__ == "__main__":
    main(sys.argv[1:])
