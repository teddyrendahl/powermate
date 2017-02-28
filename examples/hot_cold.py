"""
An example use of the PowerMateBase to play a game of Hot/Cold

Spin the powermate and watch the LED as it glows brighter the closer you get to
the target value. Press and rotate the wheel to increase the speed of travel.
Finally to exit hold and release the button for greater than two seconds
"""

import math
import asyncio
import argparse
from powermate import LedEvent, PowerMateBase

class HotPowerMate(PowerMateBase):

    press_multipler = 2

    def __init__(self, path, target=84):
        super().__init__(path)

        #Internal Warmth Parameters
        self.value    = 0
        self.target   = target

        #Turn off LED when not running
        self.on_exit()


    def on_start(self):
        #Set the LED to the starting brightness
        self._stream.send(self.warmth)


    def on_exit(self):
        #Turn off LED
        self.illuminate(0)


    @asyncio.coroutine
    def rotated(self, value, pressed=False):
        """
        Reimplementation of rotate method to reset the LED on every rotation.
        If the button is pressed while rotated move twice as fast
        """
        super().rotated(val, pressed=pressed)
        if pressed:
            value *= self.press_multiplier

        self.value += value
        return self.warmth


    @asyncio.coroutine
    def released(self, elapsed):
        """
        Reimplementation of button release to stop the demo if button is
        pressed for more than 2 seconds
        """
        super().released(elapsed)
        if elapsed > 2000:
            return Event.stop()


    @property
    def warmth(self):
        """
        The LedEvent based on the distance from the target
        """
        d = math.fabs(self.value - self.target)
        return LedEvent.percent(LedEvent.MAX_BRIGHTNESS*(1. - d/self.target))



if __name__ == '__main__':
    pm = HotPowerMate(path)
    pm()
