"""
PowerMateBase is the main driver for the powermate library. The class is built
on top of the :class:`.EventHandler` to stream events from the PowerMate USB
connection into asyncio.coroutine functions. By taking this base class, and
using it as a child of a more complex, application specific PowerMate class you
can easily map PowerMate actions into Python functions.


The main functions a wrapper can eimplement are :meth:`.on_start`,
:meth:`.on_exit`, :meth:`.rotated`, :meth:`.pressed`, and :meth:`.released`
Please not which of these are ``@asyncio.coroutine`` functions as they will
need to have that wrap to be called properly in the event loop.

In order to communicate back to the PowerMate in order to change the LED
settings for stop the loop entirely. The methods can be rewritten to send
events to return events. Many of the useful events are already available as
class methods of :class:`.LedEvent` and :class:`.Event`.
"""


import fcntl
from . import errors, event

class PowerMateBase(event.EventHandler):
    """
    Basic Powermate

    Parameters
    ----------
    path : str
        Filepath to PowerMate event stream

    loop : ``asyncio.event_loop``, optional
        Optional existing event loop if you would like to integrate multiple
        async objects
    """
    def __init__(self, path, loop=None):
        f = open(path, 'w')
        try:
            name = fcntl.ioctl(f, 0x80ff4506, chr(0)*256).decode('utf-8')
            name.replace('\x00','')
            print(name)
            if 'Griffin PowerMate' not in name:
                raise OSError("Path does not correspond to Griffin PowerMate")

        except OSError:
            raise ConnectionError("Device handle did not correspond "
                                  "to connect to a Griffin PowerMate")

        super().__init__(path, loop=loop)

    def on_start(self):
        """
        Method to be run on start of the event loop
        """
        pass


    def on_exit(self):
        """
        Method to be run on completion of the event loop
        """
        pass


    def pulse(self):
        """
        Pulse the LED on the bottom of the PowerMate

        Raises
        ------
        LoopError:
            If this is called while the device stream is running
        """
        if self.loop.is_running():
            raise errors.LoopError

        self._source.send(event.LedEvent.pulse())


    def illuminate(self, percent=100):
        """
        Illuminate the LED on the bottom of the PowerMate

        Parameters
        ----------
        brightness : float, optional
            Percentage of maximum brightness to set the LED. By default, this
            is 1., setting the LED to the brightest possible setting

        Raises
        ------
        LoopError:
            If this is called while the device stream is running
        """
        if self.loop.is_running():
            raise errors.LoopError

        self._source.send(event.LedEvent.percent(percent))


    def __call__(self):
        self.on_start()
        super().__call__()
        self.on_exit()


    def __repr__(self):
        return '<Griffin PowerMate ({})>'.format(self.path)
