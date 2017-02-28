Powermate
=========
A small Python driver for the [Griffin Powermate](https://store.griffintechnology.com/powermate) 

![Griffin Powermate](https://store.griffintechnology.com/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/n/a/na16029_powermate_1.jpg)

Setup
=====

In order to read and write to the Powermate event files on linux, you will need
to do the following (ymmv, but this should work on most modern distros).

    # /etc/udev/rules.d/40-powermate.rules
    ATTRS{product}=="Griffin PowerMate" GROUP="plugdev", SYMLINK+="input/powermate", MODE="660"
```
