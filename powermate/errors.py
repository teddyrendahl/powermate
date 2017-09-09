class EventNotImplemented(NotImplementedError):
    """
    Special exception type for non-implemented events.
    """
    pass

class PowermateIsRunning(Exception):
    """
    Exception raised when send function called at an inappropriate time
    """
    pass
