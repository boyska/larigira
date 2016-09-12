Debugging and inspecting
============================

The highly asynchronous nature of ``larigira`` might lead to difficulty in
debugging. However, ``larigira`` has some features to help you with debugging.

Debugging options
-----------------

First of all, you might want to run larigira with the environment variable
``LARIGIRA_DEBUG`` set to ``true``. ``env LARIGIRA_DEBUG=true larigira``
will do.

With this on, message logging is much more verbose. Please observe
that log messages provide information about the logger name from which the
message originated: this is typically the class name of the object.

Debug API
---------

``larigira`` also provides HTTP API to help you with debug:
``/api/debug/running``, for example, provides detailed information about
running greenlets, with several representations:

* the ``audiogens`` object will contain informations about greenlets associated
  with *scheduled* events. Here you can see its ``audiospec``, ``timespec``,
  and many other details
* the ``greenlets`` object provides a simple list of every greenlets.
  Associated with every greenlet there is as much information as possible:
  object name, documentation, etc.
* the ``greenlets_tree`` has the same information as ``greenlets``, but is
  shown as a tree: this is often easier to understand. For example, the
  ``Controller`` greenlet should have three children (``MpcWatcher``, ``Timer``
  and ``Monitor``).

A user-friendly, but more limited, visualization is available at
``/view/status/running``

Signals
---------

When ``larigira`` receives the ``ALRM`` signal, three things happen: the playlist
length is checked (as if ``CHECK_SECS`` passed); the event system "ticks" (as
if ``EVENT_TICK_SECS`` passed); the DB is reloaded from disk.
This is useful if you want to debug the event system, or if you manually
changed the data on disk. Please note that the event system will automatically
reload the DB from disk when appropriate. However, the WebUI will not, so you
might have a misleading ``/db/list`` page; send an ``ALRM`` in this case.

The same effect can be triggered performing an HTTP ``GET /rpc/refresh``.
