=========
larigira
=========

About
-------

A radio automation based on MPD. Larigira will sit right to your mpd player and
will keep your playlist never empty. It will also manage a db of "events", so
that you can schedule shows, play jingles every X minutes, etc.

Software stack
---------------

* MPD, of course
* python3

  - gevent as an async framework
  - flask to provide web interface and rpc
* tinydb as an embedded database

Why? (aka design features)
--------------------------

Reinventing a player is a bad idea. MPD provides an eccellent base.

Separating the player from "action loops" makes it easy to work on this. For
example, you can stop larigira for some minutes, and the audio will keep
playing. It also means that you can easily replace specific parts of your radio
automation.

The "continous playing" part is separated from the "events" part.  ``larigira``
can be run to perform one, the other, or both.

The "audio generation" part can be used separately by any script that you like.

Installation
-------------

Just run ``python setup.py install``. It will, of course, also work in a
virtualenv. Apart from running an MPD server, there is no additional setup.

You will find some command in your PATH now; they all begin with ``larigira``,
so the usual ``<TAB><TAB>`` is a good way to explore them ;)

The name
---------

    larigira mai la sbaglia...
    
    -- https://www.youtube.com/watch?v=K9XJkOSSdEA

