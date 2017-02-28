import os
import queue
import struct
import asyncio
import logging
import collections
from enum import Enum

logger = logging.getLogger(__name__)


EVENT_FORMAT = 'llHHi'
EVENT_SIZE   = struct.calcsize(EVENT_FORMAT)

MSC_PULSELED    = 0x01

class EventType(Enum):
    """
    Types of Events
    """
    #Internal
    PUSH   = 0x01
    ROTATE = 0x02
    MISC   = 0x04
    #API Defined
    STOP   = 0x06
    INT    = 0x08

class Event:
    """
    A Powermate Event

    Parameters
    ---------
    tv_sec : int
        Number of elapsed whole seconds

    tv_usec : int
        Remainder of elapsed time, expressed in microseconds

    type: :class:`EventType`
        Type of event

    code:
        Associated event code

    value: int
        Associated value with event

    """
    def __init__(self, tv_sec, tv_usec, type, code, value):
        self.tv_sec   = tv_sec
        self.tv_usec  = tv_usec
        self.type     = type
        self.code     = code
        self.value    = value


    @property
    def raw(self):
        """
        Converted event information expressed as binary 
        """
        return struct.pack(EVENT_FORMAT, self.tv_sec, self.tv_usec,
                       self.type.value(), self.code, self.value)


    @classmethod
    def stop(cls):
        """
        Return an Event to stop the EventStream

        Returns
        -------
        event : :class:`.LedEvent`
        """
        return cls(0, 0,  EventType.STOP, 0, 0)


    @classmethod
    def from_raw(cls, data):
        """
        Generate an ``Event`` object from packed binary data

        Parameters
        ---------
        data : int
            Binary information to unpack
        
        Returns
        -------
        event : :class:`.Event`
        """
        tv_sec, tv_usec, type, code, value = struct.unpack(EVENT_FORMAT, data)
        return cls(tv_sec, tv_usec, EventType(type), code, value)


    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               ', '.join('{}={}'.format(k, getattr(self, k))
                               for k in self.__dict__ if not k.startswith('_')))


class LedEvent(Event):
    """
    Implementation of a Powermate event specifically for sending and receiving
    instructions for LED
    
    Parameters
    ----------
    brightness : int

    speed : int

    pulse_type

    asleep

    awake : 
    """
    MAX_BRIGHTNESS  = 255
    MAX_PULSE_SPEED = 255

    def __init__(self, brightness=0, speed=0,
           pulse_type=0, asleep=0, awake=0):
        self.brightness = brightness or self.MAX_BRIGHTNESS
        self.speed      = speed
        self.pulse_type = pulse_type
        self.asleep     = asleep
        self.awake      = awake
        super().__init__(0, 0, EventType.MISC, MSC_PULSELED, 0)


    @property
    def value(self):
        """
        Packed binary instruction for the Powermate LED
        """
        return (self.brightness |
               (self.speed << 8) |
               (self.pulse_type << 17) |
               (self.asleep << 19) |
               (self.awake << 20))


    @classmethod
    def pulse(cls):
        """
        Return an Event to pulse the Powermate

        Returns
        -------
        event : :class:`.LedEvent`
        """
        return cls(speed=self.MAX_PULSE_SPEED, pulse_type=2, asleep=1, awake=1)


    @classmethod
    def max(cls):
        """
        Return an Event to set the Powermate to the maximum brightness

        Returns
        -------
        event : :class:`.LedEvent`
        """
        return cls(brightness=self.MAX_BRIGHTNESS)


    @classmethod
    def off(cls):
        """
        Return an event to turn off the Powermate LED

        Returns
        -------
        event : :class:`.LedEvent`
        """
        return cls(brightness=0)


    @classmethod
    def percent(cls, percent):
        """
        Return an event to set the Powermate to a percentage of its maximum
        brightness

        Parameters
        ----------
        percent : float
            Desired perecentage of maximum brightness

        Returns
        -------
        event : :class:`.LedEvent`
        """
        return cls(brightness=int(percent/100. * self.MAX_BRIGHTNESS))


class EventStream:
    """
    Event Stream from the Powermate

    The EventStream provides a generator object that receivies and sends data
    from the Powermate.

    Parameters
    ----------
    path : str
        Filepath to Powermate USB
    """
    _event_size = EVENT_SIZE

    def __init__(self, path):
        self.path


    def send(self, evt):
        """
        Send an event to the Powermate without viewing respsonse

        Parameters
        ----------
        evt : :class:`.Event`
            Sent event
        """
        if not isinstance(evt, Event):
            raise TypeError(evt)

        logger.debug("Sending event {} ...".format(event))

        with open(path, 'wb') as stream:
            stream.write(evt.raw)
            stream.flush()


    def __iter__(self):
        data = b''

        #Open file stream
        with open(path, 'rb') as stream:
            #Always start from EOF
            path.seek(0, os.SEEK_END)

            #Continually monitor USB
            while True:

                #When we have a full event
                if len(data) >= EVENT_SIZE:
                    #Create Event object, and delete from collected stream
                    event = Event.from_raw(data[:self._event_size])
                    logger.debug("Received event {} ...".format(event))
                    data  = data[self._event_size:]

                #Otherwise send a blank event
                else:
                   event = None

                #Send an event and check response
                ret = yield event

                if ret:
                    #Stop if stop signal was sent
                    if ret.type == EventType.STOP:
                        logger.info("Received an event to stop the stream.")
                        raise StopIteration

                    #Otherwise, send to PowerMate stream
                    else:
                        self.send(evt)


class EventHandler:
    """
    Handler for streaming Powermate Events

    Parameters
    ----------
    path : str
        Filepath to PowerMate event stream

    loop : ``asyncio.event_loop``, optional
        Optional existing event loop if you would like to integrate multiple
        async objects
    """
    #Default event size
    _event_size  = EVENT_SIZE

    #Internal State Variables
    _depressed   = None
    _rotation    = None
    _pressed     = False

    def __init__(self, path, loop=None):

        #Create Source
        self._source = EventStream(path)

        #Create asyncio event loop
        if loop is None:
            loop = asyncio.get_event_loop()
        self.loop = loop

        #Keep asyncio task to handle exceptions
        self._task = None
        self._response_stack = collections.deque([None])


    @asyncio.coroutine
    def _run(self):

        last_result = None

        try:

            yield from asyncio.sleep(0.0001, loop=self.loop)

            #Send any responses from previous events back to stream
            ret = resp_stack.pop()
            evt = self._source.send(last_result)


            #Process new events from stream
            if evt:

                logger.debug('Proccessing event')
                #On button event
                if evt.type == EventType.PUSH:

                    t = (evt.tv_sec*10**3) + (evt.tv_usec*10**-3)

                    #On press
                    if not evt.value:
                        #Change internal state to pressed
                        self._pressed   = True
                        self._rotated   = False
                        self._depressed = t

                        #Trigger pressed coroutine
                        last_result = yield from self.pressed()

                    #On release
                    else:
                        #Change internal state to released
                        self._pressed   = False

                        #Ignore if any rotation has happened
                        if self._rotated:
                            return

                        #Trigger release coroutine
                        else:
                            #Store previous depressed time, and wipe away
                            elapsed, self._depressed = t - self._depressed, None
                            #Trigger released coroutine
                            last_result = yield from self.released(elapsed)

                #On rotation event
                elif evt.type == EventType.ROTATE:
                    #Change internal state to rotated
                    self._rotated = True
                    #Trigger rotate coroutine
                    last_result = yield from self.rotate(evt.value, pressed=self._pressed)

                else:
                    raise EventNotImplemented(evt.__dict__)

        #Stop received inside event loop
        except StopIteration:
            pass

        #External Keyboard stop
        except KeyboardInterrupt:
            print("Manual interuption of PowerMate run loop")

        #Cleanup
        finally:
            self.loop.stop()


    @asyncio.coroutine
    def rotated(self, value, pressed=False):
        """
        Desired response upon rotation

        Parameters
        ----------
        value : int
            Amount of rotation seen by the Powermate

        pressed : bool
            Whether the button was depressed when rotated
        """
        logger.debug('Powermate rotated {} while pressed : {}'
                     ''.format(value, pressed))


    @asyncio.coroutine
    def pressed(self):
        """
        Desired respsone upon button press
        """
        logger.debug('Powermate pressed')


    @asyncio.coroutine
    def released(self, time):
        """
        Desired response upon button release

        Parameters
        ----------
        time ; float
            The amount of time in milliseconds that the button has been
            depressed
        """
        logger.debug('Powermate released after {} ms'.format(time))


    @asyncio.coroutine
    def stop(self):
        """
        Stop the current run
        """
        return Event.stop()


    def _clear(self):
        """
        Clear all metadata from previous run
        """
        self._task      = None
        self._rotated   = False
        self._pressed   = False
        self._depressed = None


    def __call__():

        #Clear all metadata from previous runs
        self._clear()

        #Create task and kick off loop
        self._task = self.loop.create_task(self._run())
        self.loop.run_forever()

        #Handle any exception raised during the loop
        if self._task.done and not self._task.cancelled():
            exc = self._task.exception()
            if exc is not None:
                raise exc





