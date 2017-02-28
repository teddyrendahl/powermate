import versioneer
from setuptools import (setup, find_packages)

setup(name     = 'powermate',
      version  = versioneer.get_version(),
      cmdclass = versioneer.get_cmdclass(),
      license  = 'BSD',
      author   = 'Teddy Rendahl',

      packages    = find_packages(),
      description = 'Python Driver for PowerMate USB Knob',

    )
