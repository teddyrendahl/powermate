from .          import errors
from .event     import Event, LedEvent
from .powermate import PowerMateBase

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
