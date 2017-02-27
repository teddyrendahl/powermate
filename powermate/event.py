import queue
import struct
import asyncio
import logging
import collections

from enum import Enum

EVENT_FORMAT = 'llHHi'
EVENT_SIZE   = struct.calcsize(EVENT_FORMAT)

MSC_PULSELED    = 0x01
MAX_BRIGHTNESS  = 255
MAX_PULSE_SPEED = 255

class EventType(Enum):
    """
    Types of Events
    """
    PUSH   = 0x01
    ROTATE = 0x02
    MISC   = 0x04
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


    @classmethod(cls)
    def stop(cls):
        """
        Return an Event to stop the EventStream
        
        Returns
        -------
        event : :class:`.LedEvent`
        """
        return cls(0, 0,  EventType.STOP, 0, 0)

    
    @classmethod
    def fromraw(cls, data):
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
        tv_sec, tv_usec, EventType(type), code, value = struct.unpack(EVENT_FORMAT, data)
        return cls(tv_sec, tv_usec, type, code, value)


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
    
    speed

    pulse_type

    asleep

    awake : 
    """
    def __init__(self, brightness=MAX_BRIGHTNESS, speed=0,
           pulse_type=0, asleep=0, awake=0):
        self.brightness = brightness
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
        return cls(brightness=int(percent * MAX_BRIGHTNESS))


class EventStream:
    """
    Event Stream from the Powermate

    Parameters
    ----------
    path : str
        Filepath to Powermate USB
    """
    _event_size = EVENT_SIZE

    def __init__(self, path):
        self.path


    def __iter__(self):
        data = b''

        #Open file stream
        with open(path, 'wb') as stream:
            
            #Continually monitor USB
            while True:

                #When we have a full event
                if len(data) >= EVENT_SIZE:
                    #Create Event object, and delete from collected stream
                    event = Event.fromraw(data[:self._event_size])
                    data  = data[self._event_size:]

                #Otherwise send a blank event
                else:
                   event = None

                #Send an event and check response
                ret = yield event

                if ret:
                    #Stop if stop signal was sent
                    if ret.type == EventType.STOP:
                        raise StopIteration

                    #Otherwise, send to Powermate stream
                    else:
                        stream.write(ret.raw)
                        stream.flush()
                

class EventHandler:

    _event_size = EVENT_SIZE

    def __init__(self, path, loop=None)

        #Create Source
        self._source = EventStream(path)

        #Create asyncio event loop
        if loop is None:
            loop = asyncio.get_event_loop()
        self.loop = loop

        #Keep asyncio task to handle exceptions
        self._task = None


    @asyncio.coroutine
    def _run(self):

        response_stack = collections.deque([None])

        while True:
            yield from asyncio.sleep(0.0001, loop=self.loop)

            try:
                ret = resp_stack.pop()
                msg = self._source.send(ret
    def __call__():
        #Create task and kick off loop
        self._task = self.loop.create_task(self._run())
        self.loop.run_forever()

        #Handle any exception raised during the loop
        if self._task.done and not self._task.cancelled():
            exc = self._task.exception()
            if exc is not None:
                raise exc

class EventQueue(object):
  """A thread-safe event queue which registers any number of listeners
  for an event source.

  This will store a small number of items in order for a listener to read,
  and they are then available to iterate over. If more events than the
  specified maximum are in a listener's queue, it will stop enqueueing new
  events. If for instance a listener takes a long break and max_queue_size
  is K, it will read the next K events after the sleep started (the oldest
  K events not read) and then continue to read new events. Any intermediate
  events will be dropped for that listener.

  Listeners may be simply registered by iterating over the queue, or
  through the .iterate method for more configuration.
  """
  def __init__(self, source, max_queue_size=MAX_QUEUE_SIZE):
    self.source = source
    self.queues = collections.OrderedDict()
    self._lock = threading.Lock()
    self.max_queue_size = max_queue_size

  def __iter__(self):
    return self.iterate()

  def iterate(self, max_queue_size=None):
    """Register a listener on the queue, and retrieve an iterator for them."""
    q = queue.Queue(max_queue_size or self.max_queue_size)
    key = object()
    with self._lock:
      self.queues[key] = q
    def iter_queue():
      try:
        while True:
          yield q.get()
      except GeneratorExit:
        with self._lock:
          del self.queues[key]

    return iter_queue()

  def watch(self):
    """Watch the underlying event source for events and
       send them to each registered queue."""
    for event in self.source:
      with self._lock:
        active_queues = list(self.queues.values())
      for q in active_queues:
        try:
          q.put_nowait(event)
        except queue.Full:
          pass

  def send(self, event):
    """Send an event to the underlying event source."""
    self.source.send(event)


class EventHandler(object):
  def handle_events(self, source):
    for event in source:
      try:
        return_event = self.handle_event(event)
      except EventNotImplemented:
        pass
      except Exception as e:
        traceback.print_exc()
      else:
        if return_event is not None:
          source.send(return_event)

  def handle_event(self, event):
    raise EventNotImplemented

  def push_rotate(self, rotation):
    raise EventNotImplemented('push_rotate')


class AsyncFileEventDispatcher(object):
  def __init__(self, path, event_size=EVENT_SIZE):
    self.__filesource = FileEventSource(path, event_size)
    self.__source = EventQueue(self.__filesource)
    self.__threads = []

  def add_listener(self, event_handler):
    thread = threading.Thread(target=event_handler.handle_events,
                              args=(self.__source,))
    thread.daemon = True
    thread.start()
    self.__threads.append(thread)

  def run(self):
    self.__source.watch()


class PowerMateBase(AsyncFileEventDispatcher, PowerMateEventHandler):
  def __init__(self, path, long_threshold=1000):
    AsyncFileEventDispatcher.__init__(self, path)
    PowerMateEventHandler.__init__(self, long_threshold)
    self.add_listener(self)





