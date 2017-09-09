"""
These classes make up the backbone of the powermate module. The flow of
operation starts at the :class:`.Socket`, which serves as a generator
receiving and sending commands to the file handles of the USB connnection.
These are converted into either :class:`.Event` or a more specific
implementation :class:`.LedEvent` objects. :class:`PowerMateBase` then
implements the event handling who subscribes the stream and decides which
coroutines to invoke based on the received Event and the internal state of the
PowerMate.

The only classes from this that will need to be invoked in most applications
are the event objects that you want to send back to the PowerMate. The easiest
way to create these is by using the class methods :meth:`.Event.stop`,
:meth:`LedEvent.pulse`, :meth:`.LedEvent.max`, :meth:`.LedEvent.off` and
:meth:`.LedEvent.percent`
"""
##############
#  Standard  #
##############
import os
import struct
import asyncio
import logging
import collections
from enum import Enum

##############
#  External  #
##############

##############
#   Module   #
##############
from .errors import EventNotImplemented

logger = logging.getLogger(__name__)

EVENT_FORMAT = 'llHHi'
EVENT_SIZE   = struct.calcsize(EVENT_FORMAT)

MSC_PULSELED    = 0x01
MAX_BRIGHTNESS  = 255
MAX_PULSE_SPEED = 255

class EventType(Enum):
    """
    Types of Events
    """
    #Internal
    NULL   = 0x00
    PUSH   = 0x01
    ROTATE = 0x02
    MISC   = 0x04
    #API Defined
    STOP   = 0x06

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
    def __init__(self, tv_sec, tv_usec, _type, code, value):
        self.tv_sec   = tv_sec
        self.tv_usec  = tv_usec
        self.type     = _type
        self.code     = code
        self.value    = value

    @property
    def raw(self):
        """
        Converted event information expressed as binary 
        """
        return struct.pack(EVENT_FORMAT, self.tv_sec, self.tv_usec,
                       self.type.value, self.code, self.value)

    @classmethod
    def stop(cls):
        """
        Return an Event to stop the EventStream

        Returns
        -------
        event : :class:`.Event`
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
        Intensity of LED glow, maximum is 255

    speed : int
        Speed of pulse, maximum is 255

    pulse_type : int
        Defines structure of pulse

    asleep : int 
        Defines asleep behavior

    awake : int
        Defines awake behavior
    """
    MAX_BRIGHTNESS  =  MAX_BRIGHTNESS 
    MAX_PULSE_SPEED =  MAX_PULSE_SPEED

    def __init__(self, brightness=0, speed=0,
           pulse_type=0, asleep=0, awake=0):
        super().__init__(0, 0, EventType.MISC, MSC_PULSELED, 0)
        self.brightness = brightness
        self.speed      = speed
        self.pulse_type = pulse_type
        self.asleep     = asleep
        self.awake      = awake

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

    #Silently ignore all value sets
    @value.setter
    def value(self, value):
        pass

    @classmethod
    def pulse(cls):
        """
        Return an Event to pulse the Powermate

        Returns
        -------
        event : :class:`.LedEvent`
        """
        return cls(speed=MAX_PULSE_SPEED, pulse_type=2, asleep=1, awake=1)

    @classmethod
    def max(cls):
        """
        Return an Event to set the Powermate to the maximum brightness

        Returns
        -------
        event : :class:`.LedEvent`
        """
        return cls(brightness=MAX_BRIGHTNESS)

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
        return cls(brightness=round(percent/100. * MAX_BRIGHTNESS))


class Socket:
    """
    Event Stream from the Powermate

    The EventStream provides a generator object that receivies and sends data
    from the Powermate.

    Parameters
    ----------
    path : str
        Filepath to Powermate USB
    
    Attributes
    ----------
    stream : generator
        A generator that monitors the input socket, events sent the generator
        using ``stream.send`` will also be written back into output
    """
    _event_size = EVENT_SIZE

    def __init__(self, path):
        self.path    = path
        self._output = open(self.path, 'rb')  
        self._input  = open(self.path, 'wb')  
        self.stream  = self._watch()
    
    def send(self, evt):
        """
        Send an event to the Powermate without viewing respsonse

        Parameters
        ----------
        evt : :class:`.Event`
            Sent event
        """
        #Don't send None
        if not evt:
            return
        #Only send events
        if not isinstance(evt, Event):
            raise TypeError(evt)
        logger.debug("Sending event %s ...", evt)
        #Write the value
        self._input.write(evt.raw)
        self._input.flush()

    def _watch(self):
        data  = b''
        event = None
        #Open file stream
        with self._output as stream:
            #Always start from EOF
            stream.seek(0, os.SEEK_END)
            #Continually monitor USB
            while True:
                #Send an event and check response
                ret = yield event
                try:
                    data += stream.read(self._event_size)
                except OSError as e:
                    if e.errno == 11:
                        raise ConnectionError('PowerMate disconnected')
                    else:
                        raise
                #When we have a full event
                if len(data) >= self._event_size:
                    #Create Event object, and delete from collected stream
                    try:
                        #Create an Event from the raw binary
                        event = Event.from_raw(data[:self._event_size])
                        logger.debug("Received event %s ...", event)
                    except ValueError:
                        logger.critical('Unrecognized event value')
                    #Discard last event from buffer
                    data  = data[self._event_size:]
                #Otherwise send a blank event
                else:
                    event = None
                #If we received an event back
                if ret:
                    #Stop if stop signal was sent
                    if ret.type == EventType.STOP:
                        logger.info("Received an event to stop the stream.")
                        raise StopIteration
                    #Otherwise, send to PowerMate stream
                    else:
                        self._input.write(event.raw)
                        self._input.flush()

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
        self._source = Socket(path)
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
            while True:
                yield from asyncio.sleep(0.0001, loop=self.loop)
                #Send any responses from previous events back to stream
                logger.debug("Waiting for event from PowerMate ...")
                evt = self._source.stream.send(last_result)
                #Process new events from stream
                if evt:
                    logger.debug('Proccessing event')
                    #On button event
                    if evt.type == EventType.PUSH:
                        logger.debug("Saw a push event") 
                        t = (evt.tv_sec*10**3) + (evt.tv_usec*10**-3)
                        #On press
                        if evt.value:
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
                                self._depressed = None                             
                                last_result     = None 
                            #Trigger release coroutine
                            else:
                                if not self._depressed:
                                    logger.critical("Saw a release event "
                                                    "without a pressed event")
                                    elapsed = None
                                #Store previous depressed time, and wipe away
                                else:
                                    elapsed = t - self._depressed
                                    self._depressed = None
                                #Trigger released coroutine
                                last_result = yield from self.released(elapsed)
                    #On rotation event
                    elif evt.type == EventType.ROTATE:
                        #Change internal state to rotated
                        self._rotated = True
                        #Trigger rotate coroutine
                        last_result = yield from self.rotated(evt.value,
                                                              pressed=self._pressed)
                    #Ignore empty events 
                    elif evt.type == EventType.NULL:
                        pass
                    #Bad event
                    else:
                        logger.warning("Unrecoginzed event %s", evt)
                        raise EventNotImplemented(evt.__dict__)
        #Stop received inside event loop
        except StopIteration:
            logger.info("Received StopIteration Request")
        #External Keyboard stop
        except KeyboardInterrupt:
            print("Manual interuption of PowerMate run loop")
        #Cleanup
        finally:
            logger.info("Stopping the event loop")
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
        logger.debug('Powermate rotated %s while pressed : %s',
                     value, pressed)

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
        time : float
            The amount of time in milliseconds that the button has been
            depressed


        .. note::

            This will not be called if the PowerMate is pressed and then
            rotated. Instead, this is treated as just a rotated event, with the
            pressed keyword set to True

        """
        logger.debug('Powermate released after %s ms', time)

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

    def __call__(self):
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





