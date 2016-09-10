Audiogenerators
===============

mpdrandom
---------

picks ``howmany`` song randomly from your mpd library. It follows this
strategy: it picks ``howmany`` artists from your MPD library, then picks a random song for each one

randomdir
----------

Given a directory ``path``, scan it recursively, then picks ``howmany`` random
files. No filename extensions checks are done, so beware of non-audio file in
that directory. Files are copied to ``TMPDIR`` before being returned.

static
---------

That simple: every element in ``paths`` is returned. Before doing so, they are
copied to ``TMPDIR``.

script
--------

see :doc:`audiogenerators-write`
