class PowerMateEventHandler(EventHandler):
  def __init__(self, long_threshold=1000):
    self.__rotated = False
    self.button = 0
    self.__button_time = 0
    self.__long_threshold = long_threshold

  def handle_event(self, event):
    if event.type == PUSH:
      time = event.tv_sec * 10 ** 3 + (event.tv_usec * 10 ** -3)
      self.button = event.value
      if event.value:  # button depressed
        self.__button_time = time
        self.__rotated = False
      else:
        # If we have rotated this push, don't execute a push
        if self.__rotated:
          return
        if time - self.__button_time > self.__long_threshold:
          return self.long_press()
        else:
          return self.short_press()
    elif event.type == ROTATE:
      if self.button:
        self.__rotated = True
        return self.push_rotate(event.value)
      else:
        return self.rotate(event.value)

    raise EventNotImplemented('unknown')

  def short_press(self):
    raise EventNotImplemented('short_press')

  def long_press(self):
    # default to short press if long press is not defined
    return self.short_press()

  def rotate(self, rotation):
    raise EventNotImplemented('rotate')
