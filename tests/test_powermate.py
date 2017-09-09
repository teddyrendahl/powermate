##############
#  Standard  #
##############
import io
import asyncio
import tempfile

##############
#  External  #
##############
import pytest

##############
#   Module   #
##############
import powermate
from powermate.event import Event, EventType

events = [
    #Regular Push
    Event(23434040, 340340, EventType.PUSH, 0, 1),
    Event(23435040, 340340, EventType.PUSH, 1, 0),
    #Regular Push
    Event(23436040, 340340, EventType.PUSH, 1, 1),
    Event(23437040, 340340, EventType.PUSH, 1, 0),
    #Twist
    Event(23438040, 340340, EventType.PUSH, 1, 1),
    Event(23438140, 340340, EventType.ROTATE, 1, 2),
    Event(23438240, 340340, EventType.ROTATE, 1, 3),
    Event(23439040, 340340, EventType.PUSH, 1, 0),
    #Rotate
    Event(23441040, 340340, EventType.ROTATE, 1, 2),
    #Long Push
    Event(23442040, 340340, EventType.PUSH, 1, 1),
    Event(53443040, 340340, EventType.PUSH, 1, 0)]

class PseudoStream(io.BytesIO):
    """
    BytesIO object that continually adds new events
    """
    def __init__(self, stream, *args, **kwargs):
        self.stream = stream
        super().__init__(*args, **kwargs)

    def read(self, *args, **kwargs):
        return self.stream.pop(0).raw


class CountingPowerMate(powermate.PowerMateBase):
    """
    PowerMate that counts the Events that happen
    """
    def __init__(self, path, loop=None):
        #Store actions
        self.presses        = 0
        self.releases       = 0
        self.rotations      = 0
        self.twists         = 0
        self.twist_releases = 0 
        super().__init__(path, loop=loop)
        #Replace output with PseudoStream
        self._source._output = PseudoStream(events)

    @asyncio.coroutine
    def pressed(self):
        super().pressed()
        self.presses += 1

    @asyncio.coroutine
    def rotated(self, value, pressed):
        super().rotated(value, pressed=pressed)
        if pressed:
            self.twists += value
        else:
            self.rotations += value

    @asyncio.coroutine
    def released(self, time, rotated):
        super().released(time)
        self.releases +=  1
        self.twist_releases += int(rotated)
        if time > 1000000:
            return Event.stop()

@pytest.fixture(scope='function')
def counting_powermate():
    with tempfile.NamedTemporaryFile() as tmp:
        yield CountingPowerMate(tmp.name)

def test_powermatebase(counting_powermate):
    #Load PowerMate
    #Run through fake event stream
    counting_powermate.run()
    #Check our count of actions
    assert counting_powermate.presses        == 4
    assert counting_powermate.releases       == 4
    assert counting_powermate.rotations      == 2
    assert counting_powermate.twists         == 5
    assert counting_powermate.twist_releases == 1
