Installation
=============

Installing larigira is quite simple. You can install latest version from PyPI
using ``pip install larigira``. Or you can ``git clone
https://github.com/boyska/larigira.git`` and run ``python setup.py install``.
As always, the usage of a virtualenv is recommended.

The only supported python version is 3.4.

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
``$HOME/.mpd/socket``. If you don't do this, you'll find many::

    15:37:10|ERROR[Player:93] Cannot insert song file:///tmp/larigira.1002/audiogen-randomdir-8eoklcee.mp3
    Traceback (most recent call last):
      File "/home/user/my/ror/larigira/larigira/mpc.py", line 91, in enqueue
        mpd_client.addid(uri, insert_pos)
      File "/home/user/.virtualenvs/larigira3/lib/python3.5/site-packages/python_mpd2-0.5.5-py3.5.egg/mpd.py", line 629, in decorator
        return wrapper(self, name, args, bound_decorator(self, returnValue))
      File "/home/user/.virtualenvs/larigira3/lib/python3.5/site-packages/python_mpd2-0.5.5-py3.5.egg/mpd.py", line 254, in _execute
        return retval()
      File "/home/user/.virtualenvs/larigira3/lib/python3.5/site-packages/python_mpd2-0.5.5-py3.5.egg/mpd.py", line 623, in decorator
        return function(self, *args, **kwargs)
      File "/home/user/.virtualenvs/larigira3/lib/python3.5/site-packages/python_mpd2-0.5.5-py3.5.egg/mpd.py", line 384, in _fetch_item
        pairs = list(self._read_pairs())
      File "/home/user/.virtualenvs/larigira3/lib/python3.5/site-packages/python_mpd2-0.5.5-py3.5.egg/mpd.py", line 311, in _read_pairs
        pair = self._read_pair(separator)
      File "/home/user/.virtualenvs/larigira3/lib/python3.5/site-packages/python_mpd2-0.5.5-py3.5.egg/mpd.py", line 302, in _read_pair
        line = self._read_line()
      File "/home/user/.virtualenvs/larigira3/lib/python3.5/site-packages/python_mpd2-0.5.5-py3.5.egg/mpd.py", line 291, in _read_line
        raise CommandError(error)
    mpd.CommandError: [400] {addid} Access denied

