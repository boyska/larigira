Installation
=============

Installing larigira is quite simple. You can install latest version from PyPI
using ``pip install larigira``. Or you can ``git clone
https://github.com/boyska/larigira.git`` and run ``python setup.py install``.
As always, the usage of a virtualenv is recommended.

The only supported python version is 2.7.

Configuration
---------------

larigira use MPD in a peculiar way. It can use mpd internal library, but it can
also work with "regular" local files, outside of the library. To do so,
however, it requires you to connect to MPD through the UNIX socket instead of
the TCP port.

So how to create this setup?
inside ``~/.mpdconf``, add the following line::

    bind_to_address "~/.mpd/socket"

For larigira, you need to set the ``MPD_HOST`` environment variable to
``$HOME/.mpd/socket``.
