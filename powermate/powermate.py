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
            name = fcntl.ioctl(x, 0x80ff4506, chr(0)*256)
            name.replace(chr(0),'')

            if name != 'Griffin PowerMate':
                raise OSError

        except OSError:
            raise ConnectionError("Device handle did not correspond "
                                  "to connect to a Griffin PowerMate")



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

        self._stream.send(event.LedEvent.pulse())


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

        self._stream.send(event.LedEvent.brightness(percentage))


    def __call__(self):
        self.on_start()
        super.__call__()
        self.on_exit()


    def __repr__(self):
        return '<Griffin PowerMate ({})>'.format(self.path)
