##############
#  Standard  #
##############

##############
#  External  #
##############

##############
#   Module   #
##############
import powermate

#Raw Event Binary
raw_evt = b'\x8f\n\x16\x00\x00\x00\x00\x00\x84\x10\x18'\
          b'\xb6\x00\x00\x00\x00\x01\x00\x00\x01\x01\x00'\
          b'\x00\x00'

def test_stop():
    #Generate a STOP Event
    evt = powermate.Event.stop()
    assert evt.type == powermate.event.EventType.STOP

def test_raw():
    #Convert an event back to binary
   evt = powermate.Event(1444495,3055030404,
                         powermate.event.EventType.PUSH,
                         256, 1)
   assert evt.raw == raw_evt
                      
def test_from_raw():
    #Convert binary to an Event
    evt = powermate.Event.from_raw(raw_evt) 
    assert evt.tv_sec  == 1444495
    assert evt.tv_usec == 3055030404
    assert evt.type    == powermate.event.EventType.PUSH
    assert evt.code    == 256
    assert evt.value   == 1

def test_pulse():
    #Generate a pulse Event
    evt = powermate.LedEvent.pulse()
    assert evt.speed == 255
    assert evt.asleep == 1
    assert evt.awake == 1
    assert evt.pulse_type == 2
    assert evt.type == powermate.event.EventType.MISC

def test_max():
    #Generate an Event for the maximum brightness of the LED
    evt = powermate.LedEvent.max()
    assert evt.brightness == 255
    assert evt.type == powermate.event.EventType.MISC

def test_off():
    #Generate an Event to turn the LED off
    evt = powermate.LedEvent.off()
    assert evt.brightness == 0
    assert evt.type == powermate.event.EventType.MISC

def test_percent():
    #All the way off
    evt = powermate.LedEvent.percent(0)
    assert evt.brightness == 0
    assert evt.type == powermate.event.EventType.MISC
    #Half way on
    evt = powermate.LedEvent.percent(50)
    assert evt.brightness == 128
    #Quarter of the way on
    evt = powermate.LedEvent.percent(25)
    assert evt.brightness == 64

def test_socket_send(pseudo_socket):
    #Send an event to a binary file
    evt = powermate.Event.stop()
    pseudo_socket.send(evt)
    pseudo_socket._input.seek(0)
    #Assert we translated the whole Event
    assert pseudo_socket._input.read() == evt.raw
