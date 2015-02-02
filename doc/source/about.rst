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
simplicity and flexibility.

Code structure and core concepts
-----------------------------------

The code is heavily based on gevent.

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
