Write your own audiogenerator
=============================

It's easy to have situations where you want to run your own custom
audiogenerator. Fetching music with some very custom logic? Checking RSS
feeds? Whatever. There are two main strategies to add audiogenerators to
``larigira``: scripts and setuptools entrypoints. Scripts are easier.
setuptools entrypoints are somewhat "tidier". We suggest writing entrypoints if
you want to distribute your code somehow. If your script is so custom that only
makes sense to you, a script can be enough.

writing a script
-----------------

a script is an executable file. The programming language is completely to your
choice: bash, perl, python, compiled C code, ``larigira`` doesn't care.
It must be in a specific directory (``~/.config/larigira/scripts/``), be
executable (as in ``chmod +x``), and be owned by the same user running
larigira.

When executed, this script must output URIs, one per line. Only UTF-8 is
supported as encoding. The script should expect limited environment (for
security reaons). Please also see :mod:`larigira.audiogen_script` for more
details.

writing an audiogen entrypoint
------------------------------

TODO
