Powermate Python Driver
=======================
.. image:: https://travis-ci.org/teddyrendahl/powermate.svg?branch=master
    :target: https://travis-ci.org/teddyrendahl/powermate

.. image:: https://codecov.io/gh/teddyrendahl/powermate/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/teddyrendahl/powermate

.. image:: https://landscape.io/github/teddyrendahl/powermate/master/landscape.svg?style=flat
   :target: https://landscape.io/github/teddyrendahl/powermate/master

A small Python driver for using the `Griffin Powermate <https://store.griffintechnology.com/powermate/>`_ in Linux 

.. image:: https://store.griffintechnology.com/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/n/a/na16029_powermate_1.jpg


Setup
-----
In order to read and write to the Powermate event files on Linux, you will need
to add the following ``udev`` rule. The choice of symlink name is up to you,
but should be memorable as this how you point the API to the correct USB port

.. code::

    # /etc/udev/rules.d/40-powermate.rules
    ATTRS{product}=="Griffin PowerMate" GROUP="plugdev", SYMLINK+="input/powermate", MODE="666"

Use Cases
---------
The main class in the powermate driver is the ``powermate.PowerMateBase`` This
wraps the event handling streams into rewritable Python functions. Simply
create a new class who inherits from ``PowerMateBase`` and rewrite the
``rotated``, ``pressed`` and ``released`` to map the PowerMate actions to
commands. It is important to note that these are used in the ``asycnio`` run
loop, so they must have the ``@asyncio.coroutine`` function wrap

.. literalinclude:: /../../examples/simple.py
    :pyobject: SimplePowerMate

Complex interactions between driver actions and the PowerMate are possible by
creating coroutines that return events. For instance, the ``pressed`` function
in this [example]( sends an ``.Event.stop`` back to the PowerMate to indicate
we are done listening to the USB connection.

After you have created your PowerMate, simply call the class and the listener
will begin watching the USB connection for PowerMate events. If you used the
``udev`` rules above it should look like this

.. code::

    #Instantiate
    pm = SimplePowerMate('/dev/input/powermate')
    #Run
    pm()
