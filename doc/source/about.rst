About
========

What does it do
---------------

larigira integrates with MPD (Music Player Daemon) and prevents your playlist
from running empty. It also has powerful support for "events": audio that must be played at some time.

Features
---------

* Simple to install
* WebUI
* modular event system

Architecture
-------------

larigira delegates all the music playing business to MPD.
It relies on ``tinydb`` as a db: it's actually just a json file, to achieve
simplicity and flexibility. By default it is stored in ``~/.config/larigira/db.json``

Code structure and core concepts
-----------------------------------

The code is heavily based on gevent: almost everything is a greenlet.

alarm
  An alarm is a specification of timings. It is "something that can generate
  times". For example ``{ 'kind': 'single', 'timestamp': 1234567890 }``
  generates a single time (February 14, 2009 00:31:00), while
  ``{ 'kind': 'frequency', 'interval': 10, 'start': 1234567890 }`` generates
  infinite times, one every 10 seconds, starting from February 14, 2009
  00:31:00.

action
  An action is a specification of audio. It is "something that can generate a
  list of audio files".
  For example, ``{ 'kind': 'randomdir', 'paths': ['/my/dir', '/other/path'] }``
  will pick a random file from one of the two paths.

event
  An event is an alarm plus a list of actions. At given times, do those things

The main object is :class:`larigira.mpc.Controller`, which in turn uses :class:`larigira.mpc.Player` to control MPD. How does it know what to do? there are two main flows: the continous playlist filling and the alarm
system.

Continous playlist
~~~~~~~~~~~~~~~~~~

:class:`larigira.mpc.Controller` has a "child" called :class:`larigira.mpc.MpcWatcher`. It watches for events on
the playlist; when the playlist is changed it notifies Controller, which in turn will check if the playlist has
enough songs. If that's the case, it will run an audiogenerator, and add the resulting audio at the bottom of the playlist.

Alarm system
~~~~~~~~~~~~

There is a DB. The lowest level is handled by TinyDB. :class:`larigira.event.EventModel` is a thin layer on
it, providing more abstract functions.

There is a :class:`Monitor <larigira.event.Monitor>`, which is something that, well, "monitors" the DB and
schedule events appropriately. It will check alarms every ``EVENT_TICK_SECS`` seconds, or when larigira received
a ``SIGALRM`` (so ``pkill -ALRM larigira`` might be useful for you).

You can view scheduled events using the web interface, at ``/view/status/running``. Please note that you will
only see *scheduled* events, which are events that will soon be added to playlist. That page will not give you
information about events that will run in more than ``2 * EVENT_TICK_SECS`` seconds (by default, this amounts
to 1 minute).
