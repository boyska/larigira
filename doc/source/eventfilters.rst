EventFilters
================

What is an event filter? It is a mechanism to filter songs before adding them to the playlist.
Why is it any useful? To implement something better than a priority system!

Real world example: you have many events. Some are very long ("shows"), some are short ("jingle"). If you
have a long show of 2hours, and a jingle every 15minutes, then at the end of your jingle you'll find 8 jingle
stacked. That's bad! How to fix it? There are many solutions, none of them is very general or suits every
need. EventFilter is a mechanism to have multiple filters running serially to find a reason to exclude an
event.

Using an event filter
-----------------------

larigira provides some basic filter. A simple example can be "maxwait". The principle is just "don't
add new events if the current playing song still needs more than X seconds to finish". Setting this to, for
example, 15 minutes, would have found only one jingle in the previous example. Great job!

However, it wouldn't be very kind of long shows. If you have two long shows, each 2h long, scheduled let's say
at 8:00 and 9:30. Now the second show won't start, because there is 30min remaining, and the maxwait is set
to 15min. If you have this solution, maybe *percentwait* will better suit your needs. Set this to 200%, and
a jingle can wait up to twice its own duration. This is like setting maxtime=4hours for the long shows, but
maxtime=1minute for jingles. Nice!

Examples
----------

Fixed wait
~~~~~~~~~~~~~~~

This snippet will configure larigira to wait a maximum of 5 minutes::

    LARIGIRA_EVENT_FILTERS='["maxwait"]'
    LARIGIRA_EF_MAXWAIT_SEC=300

(60*5 = 300seconds). This will basically cancel any event that finds a currently playing audio not at its end.
It can be recommended if you have very accurate timing or don't care about "losing" shows because the one
preceding it lasted for too long.

Relative wait
~~~~~~~~~~~~~~~~

This will configure larigira so that a 1-minute jingle can wait for a maximum of 4minutes, while a 20minutes
event can wait up to 1h20min::
    
    LARIGIRA_EVENT_FILTERS='["percentwait"]'
    LARIGIRA_EF_MAXWAIT_PERC=400

In fact, ``400`` means 400%, that is 4 times the lenght of what we're adding

Write your own
----------------

You probably have some very strange usecase here. Things to decide based on your custom naming convention,
time of the day, moon phase, whatever. So you can and should write your own eventfilter. It often boils down
to very simple python functions and configuration of an entrypoint for the `larigira.eventfilter` entrypoint.

