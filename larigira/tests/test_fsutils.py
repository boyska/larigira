from larigira.fsutils import shortname


def test_shortname_self():
    '''sometimes, shortname is just filename without extension'''
    assert shortname('/tmp/asd/foo.bar') == 'foo'


def test_shortname_has_numbers():
    '''shortname will preserve numbers'''
    assert shortname('/tmp/asd/foo1.bar') == 'foo1'


def test_shortname_has_no_hyphen():
    '''shortname will not preserve hyphens'''
    assert shortname('/tmp/asd/foo-1.bar') == 'foo1'
