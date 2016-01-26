#!/usr/bin/python


# __author__ = 'ThinkPad'

import time

from phue import Bridge
import schedule

IP_BRIDGE = '192.168.178.24'

START_BRIGHTNESS = 254
START_COLORTEMP = 369
START_SATURATION = 144
START_XY = [0.4595, 0.4105]


class Hue():
    def main(self):
        b = Bridge(IP_BRIDGE)

        b.connect()
        lights = b.lights

        for light in lights:

            # pdb.set_trace()
            if light.brightness == START_BRIGHTNESS and light.colortemp == START_COLORTEMP and light.saturation == START_SATURATION and light.xy == START_XY:
                light.brightness = 207
                light.colortemp = 459
                light.colortemp_k = 2179
                light.saturation = 209
                light.saturation = 100
                light.xy = [0.509, 0.4149]


if __name__ == '__main__':

    schedule.every(5).seconds.do(Hue().main)

    while 1:
        schedule.run_pending()

        time.sleep(1)
