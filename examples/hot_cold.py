"""
An example use of the PowerMateBase to play a game of Hot/Cold

Spin the powermate and watch the LED as it glows brighter the closer you get to
the target value.  Finally to exit hold and release the button for greater than
two seconds
"""

import math
import asyncio
import argparse
from powermate import LedEvent, PowerMateBase

class HotPowerMate(PowerMateBase):
    """
    Hot/Cold game for PowerMate

    Parameters
    ----------
    path : str

    target : int, optional
        Target value that will have the brightest LED setting
    """
    def __init__(self, path, target=50):
        super().__init__(path)
        #Internal Warmth Parameters
        self.value    = 0
        self.target   = target
        #Turn off LED when not running
        self.on_exit()

    def on_start(self):
        """
        Set the LED to the starting brightness
        """
        #Set the LED to the starting brightness
        self._stream.send(self.warmth)

    def on_exit(self):
        """
        Turn of the LED when the loop is not running
        """
        self.illuminate(0)

    @asyncio.coroutine
    def rotated(self, value, pressed=False):
        """
        Reimplementation of rotate method to reset the LED on every rotation.
        """
        self.value += value
        return self.warmth

    @asyncio.coroutine
    def released(self, elapsed, rotated):
        """
        Reimplementation of button release to stop the demo if button is
        pressed for more than 2 seconds
        """
        if elapsed > 2000:
            return Event.stop()

    @property
    def warmth(self):
        """
        The LedEvent based on the distance from the target
        """
        #Distance from target
        d = math.fabs(self.value - self.target)
        return self.illuminate(1. - d/self.target)
