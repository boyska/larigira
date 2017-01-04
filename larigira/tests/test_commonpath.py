import pytest

from larigira.unused import old_commonpath


def test_same():
    assert old_commonpath(['/foo/bar', '/foo/bar/']) == '/foo/bar'


def test_prefix():
    assert old_commonpath(['/foo/bar', '/foo/zap/']) == '/foo'
    assert old_commonpath(['/foo/bar/', '/foo/zap/']) == '/foo'
    assert old_commonpath(['/foo/bar/', '/foo/zap']) == '/foo'
    assert old_commonpath(['/foo/bar', '/foo/zap']) == '/foo'


try:
    from os.path import commonpath
except ImportError:
    pass  # TODO: log the fact and clarify
else:
    # these tests are only available on python >= 3.5. That's fine though, as
    # our CI will perform validation of those cases to see if they match python
    # behavior
    @pytest.fixture(params=['a', 'a/', 'a/b', 'a/b/', 'a/b/c', ])
    def relpath(request):
        return request.param

    @pytest.fixture
    def abspath(relpath):
        return '/' + relpath

    @pytest.fixture(params=['', '/'])
    def slashed_abspath(abspath, request):
        return '%s%s' % (abspath, request.param)
    slashed_abspath_b = slashed_abspath

    @pytest.fixture
    def abspath_couple(slashed_abspath, slashed_abspath_b):
        return (slashed_abspath, slashed_abspath_b)

    def test_abspath_match(abspath_couple):
        assert commonpath(abspath_couple) == old_commonpath(abspath_couple)

    @pytest.fixture(params=['', '/'])
    def slashed_relpath(relpath, request):
        s = '%s%s' % (relpath, request.param)
        if s:
            return s
    slashed_relpath_b = slashed_relpath

    @pytest.fixture
    def relpath_couple(slashed_relpath, slashed_relpath_b):
        return (slashed_relpath, slashed_relpath_b)

    def test_relpath_match(relpath_couple):
        assert commonpath(relpath_couple) == old_commonpath(relpath_couple)
