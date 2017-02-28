"""
A simple instantiation of the PowerMate class to print actions as they occur
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
        print('Done watching the PowerMate')


    @asyncio.coroutine
    def rotated(self, val, pressed=False):
        """
        Run when the PowerMate is rotated
        """
        super().rotated(val, pressed=pressed)
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
        super().pressed()
        print("PowerMate has been pressed")

    
    @asyncio.coroutine
    def released(self, elapsed):
        """
        Run when the PowerMate is pressed
        """
        super().released(elapsed)
        print("PowerMate has been released after {} ms")
        if elapsed > 1000:
            return Event.stop()


if __name__ == "__main__":

    pm = SimplePowerMate()
    pm()
