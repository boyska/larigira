from pathlib import Path

from larigira.audiogen_randomdir import candidates


def P(pypathlocal):
    return Path(str(pypathlocal))


def test_txt_files_are_excluded(tmpdir):
    p = tmpdir.join("foo.txt")
    p.write('')
    assert len(candidates([P(p)])) == 0
    assert len(candidates([P(tmpdir)])) == 0


def test_nested_txt_files_are_excluded(tmpdir):
    p = tmpdir.mkdir('one').mkdir('two').join("foo.txt")
    p.write('')
    assert len(candidates([P(p)])) == 0
    assert len(candidates([P(tmpdir)])) == 0


def test_mp3_files_are_considered(tmpdir):
    p = tmpdir.join("foo.mp3")
    p.write('')
    assert len(candidates([P(p)])) == 1
    assert len(candidates([P(tmpdir)])) == 1


def test_nested_mp3_files_are_considered(tmpdir):
    p = tmpdir.mkdir('one').mkdir('two').join("foo.mp3")
    p.write('')
    assert len(candidates([P(p)])) == 1
    assert len(candidates([P(tmpdir)])) == 1


def test_same_name(tmpdir):
    '''file with same name on different dir should not be confused'''
    p = tmpdir.mkdir('one').mkdir('two').join("foo.mp3")
    p.write('')
    p = tmpdir.join("foo.mp3")
    p.write('')

    assert len(candidates([P(tmpdir)])) == 2


def test_unknown_mime_ignore(tmpdir):
    p = tmpdir.join("foo.???")
    p.write('')
    assert len(candidates([P(tmpdir)])) == 0


def test_unknown_mime_nocrash(tmpdir):
    p = tmpdir.join("foo.???")
    p.write('')
    p = tmpdir.join("foo.ogg")
    p.write('')
    assert len(candidates([P(tmpdir)])) == 1
