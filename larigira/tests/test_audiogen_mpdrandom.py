from __future__ import print_function
from gevent import monkey
monkey.patch_all(subprocess=True)

import pytest

from larigira.audiogen_mpdrandom import generate_by_artist


@pytest.fixture
def simplerandom():
    return {
    }


def test_accepted_syntax(simplerandom):
    '''Check the minimal needed configuration for mpdrandom'''
    generate_by_artist(simplerandom)
