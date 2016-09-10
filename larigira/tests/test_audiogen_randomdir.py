from gevent import monkey
monkey.patch_all(subprocess=True)

import pytest

from larigira.audiogen_randomdir import generate


@pytest.fixture
def simplerandom():
    return {
        'paths': '/tmp/do/not/exist',
    }


def test_accepted_syntax(simplerandom):
    '''Check the minimal needed configuration for randomdir'''
    generate(simplerandom)
