import io
import pytest
import powermate

@pytest.fixture(scope='module')
def pseudo_socket():
    s = powermate.event.Socket('tests/stream.txt')
    s._input  = io.BytesIO()
    s._output = io.BytesIO()
    return s
