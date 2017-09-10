"""
PowerMateBase is the main driver for the powermate library. The class is built
on top of the :class:`.EventHandler` to stream events from the PowerMate USB
connection into asyncio.coroutine functions. By taking this base class, and
using it as a parent of a more complex, application specific PowerMate class you
can easily map PowerMate actions into Python functions.

The main functions a wrapper can reimplement are :meth:`.on_start`,
:meth:`.on_exit`, :meth:`.rotated`, :meth:`.pressed`, and :meth:`.released`
Please note which of these are ``@asyncio.coroutine`` functions as they will
need to have that wrap to be called properly in the event loop.

When these functions are called while the event loop is running, the return
values are stored, converted to binary and sent back to the PowerMate. This
allows you to implement logic in each coroutine to manipulate the LED on the
bottom of the Powermate, or stop the loop entirely. Many of the useful events
are already available as class methods of :class:`.LedEvent` and
:class:`.Event`.
"""
##############
#  Standard  #
##############

##############
#  External  #
##############

##############
#   Module   #
##############
from .event  import LedEvent, EventHandler

class PowerMateBase(EventHandler):
    """
    Basic Powermate

    A subclass of :class:`EventHandler` with a number of conveinence methods
    added for ease of use. By using :meth:`.rotate`, :meth:`.pressed` and
    :meth:`.released` you can map five distinct events into Python functions:

    - Pressing the PowerMate down
    - Releasing the PowerMate
    - Rotating the PowerMate
    - Rotating the PowerMate while pressed
    - Releasing the PowerMate after a rotation

    Parameters
    ----------
    path : str
        Filepath to PowerMate event stream

    loop : ``asyncio.event_loop``, optional
        Optional existing event loop if you would like to integrate multiple
        async objects
    """
    def on_start(self):
        """
        Method to be called prior to thestart of thedevent loop
        """
        pass

    def on_exit(self):
        """
        Method to be called after the completion of the event loop
        """
        pass

    def pulse(self):
        """
        Pulse the LED on the bottom of the PowerMate
        
        If the loop is running this simply returns an LedEvent, otherwise
        this handles writing the Event into the stream
        """
        evt = LedEvent.pulse()
        #Don't send the event while loop is running
        if not self.loop.is_running():
            self._source.send(evt)
        return evt

    def illuminate(self, percent=100):
        """
        Illuminate the LED on the bottom of the PowerMate
        
        If the loop is running this simply returns an LedEvent, otherwise
        this handles writing the Event into the stream

        Parameters
        ----------
        brightness : float, optional
            Percentage of maximum brightness to set the LED. By default, this
            is 1., setting the LED to the brightest possible setting
        """
        evt = LedEvent.percent(percent)
        #Don't send the event while loop is running
        if not self.loop.is_running():
            self._source.send(evt)
        return evt

    def run(self):
        """
        Stream events from the PowerMate
        """
        self.on_start()
        super().__call__()
        self.on_exit()

    __call__ = run

    def __repr__(self):
        return '<Griffin PowerMate ({})>'.format(self._source.path)
