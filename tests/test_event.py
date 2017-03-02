import pytest
import powermate

def test_stop():
    evt = powermate.Event.stop()
    assert evt.type == powermate.event.EventType.STOP

def test_raw():
   evt = powermate.Event(1444495,3055030404,
                         powermate.event.EventType.PUSH,
                         256, 1)
   assert evt.raw ==  '\x8f\n\x16\x00\x00\x00\x00\x00\x84\x10\x18'\
                      '\x00\x00\x00\x00\x00\x01\x00\x00\x01\x01\x00'\
                      '\x00\x00' 

def test_from_raw():
    evt = powermate.Event.from_raw( '\x8f\n\x16\x00\x00\x00\x00\x00'\
                                    '\x84\x10\x18\xb6\x00\x00\x00\x00'\
                                    '\x01\x00\x00\x01\x01\x00\x00\x00')
    assert evt.tv_sec  == 1444495
    assert evt.tv_usec == 3055030404
    assert evt.type    == powermate.event.EventType.PUSH
    assert evt.code    == 256
    assert evt.value   == 1


def test_pulse():
    evt = powermate.LedEvent.pulse()
    assert evt.speed == 255
    assert evt.asleep == 1
    assert evt.awake == 1
    assert evt.pulse_type == 2
    assert evt.type == powermate.event.EventType.MISC

def test_max():
    evt = powermate.LedEvent.max()
    assert evt.brightness == 255
    assert evt.type == powermate.event.EventType.MISC

def test_off():
    evt = powermate.LedEvent.off()
    assert evt.brightness == 0
    assert evt.type == powermate.event.EventType.MISC

def test_percent():
    evt = powermate.LedEvent.percent(0)
    assert evt.brightness == 0
    assert evt.type == powermate.event.EventType.MISC

    evt = powermate.LedEvent.percent(50)
    assert evt.brightness == 128
    
    evt = powermate.LedEvent.percent(25)
    assert evt.brightness == 64

def test_socket_send(pseudo_socket):
    evt = powermate.Event.stop()
    pseudo_socket.send(evt)
    pseudo_socket._input.seek(0)
    assert pseudo_socket._input.read() == evt.raw


def test_generator(pseudo_socket):
    evt_1 = powermate.Event(141244, 2342340,
                            powermate.event.EventType.PUSH,
                            256, 1)
    evt_2 = powermate.Event(141344, 234440,
                            powermate.event.EventType.ROTATE,
                            0, 2)
    evt_3 = powermate.Event.stop()
    for evt in (evt_1, evt_2, evt_3):
        pseudo_socket._input.write(evt.raw)
    assert pseudo_socket.stream.send(None) == None
    pseudo_socket._input.seek(0)
    assert evt_1 == pseudo_socket.stream.send(None)
    assert evt_2 == pseudo_socket.stream.send(None)
    assert evt_3 == pseudo_socket.stream.send(None)
