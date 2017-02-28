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
