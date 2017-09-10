"""
A simple instantiation of the PowerMate class to print the actions of the USB
device as they happen. The methods also return :class:`.LedEvent` objects to
light the bottom of the Powermate when pressed and turn it off when released
"""
import asyncio
from powermate import Event, PowerMateBase


class SimplePowerMate(PowerMateBase):

    def on_start(self):
        """
        Run once when the call loop is instantiated
        """
        print('Starting to watch the PowerMate')

    def on_exit(self):
        """
        Run when the event loop is done running
        """
        print('Done watching the PowerMate')

    @asyncio.coroutine
    def rotated(self, val, pressed):
        """
        Run when the PowerMate is rotated
        """
        if pressed:
            print("PowerMate has been pressed and rotated {} counts ..."
                  "".format(val))
        else:
            print("PowerMate has been rotated {} counts ..."
                  "".format(val))

    @asyncio.coroutine
    def pressed(self):
        """
        Run when the PowerMate is pressed
        """
        print("PowerMate has been pressed")
        return self.illuminate(100)

    @asyncio.coroutine
    def released(self, elapsed, rotated):
        """
        Run when the PowerMate is released
        """
        super().released(elapsed)
        print("PowerMate has been released after {} ms".format(elapsed))
        if rotated:
            print("The PowerMate was rotated during this time")
        if elapsed > 2500:
            return Event.stop()
        else:
            return self.illuminate(0)
