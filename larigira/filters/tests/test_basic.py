from larigira.filters.basic import maxwait, percentwait


def matchval(d):
    def mocked(input_):
        if input_ in d:
            return d[input_]
        for k in d:
            if k in input_:  # string matching
                return d[k]
        raise Exception("This test case is bugged! No value for %s" % input_)
    return mocked


durations = dict(one=60, two=120, three=180, four=240, ten=600, twenty=1200,
                 thirty=1800, nonexist=None)
dur = matchval(durations)


def normalize_ret(ret):
    if type(ret) is bool:
        return ret, ''
    return ret


def mw(*args, **kwargs):
    return normalize_ret(maxwait(*args, **kwargs))


def pw(*args, **kwargs):
    kwargs['getdur'] = dur
    return normalize_ret(percentwait(*args, **kwargs))


def test_maxwait_nonpresent_disabled():
    ret = mw([], {}, {})
    assert ret[0] is True


def test_maxwait_explicitly_disabled():
    ret = mw([], {}, {'EF_MAXWAIT_SEC': 0})
    assert ret[0] is True


def test_maxwait_ok():
    ret = mw([], {'status': {'time': '250:300'}}, {'EF_MAXWAIT_SEC': 100})
    assert ret[0] is True


def test_maxwait_exceeded():
    ret = mw([], {'status': {'time': '100:300'}}, {'EF_MAXWAIT_SEC': 100})
    assert ret[0] is False


def test_maxwait_limit():
    ret = mw([], {'status': {'time': '199:300'}}, {'EF_MAXWAIT_SEC': 100})
    assert ret[0] is False
    ret = mw([], {'status': {'time': '200:300'}}, {'EF_MAXWAIT_SEC': 100})
    assert ret[0] is True
    ret = mw([], {'status': {'time': '201:300'}}, {'EF_MAXWAIT_SEC': 100})
    assert ret[0] is True


def test_percentwait_nonpresent_disabled():
    ret = pw([], {}, {})
    assert ret[0] is True


def test_percentwait_explicitly_disabled():
    ret = pw([], {}, {'EF_MAXWAIT_PERC': 0})
    assert ret[0] is True


def test_percentwait_ok():
    # less than one minute missing
    ret = pw(dict(uris=['file:///oneminute.ogg']),
             {'status': {'time': '250:300'}},
             {'EF_MAXWAIT_PERC': 100})
    assert ret[0] is True

    # more than one minute missing
    ret = pw(dict(uris=['file:///oneminute.ogg']),
             {'status': {'time': '220:300'}},
             {'EF_MAXWAIT_PERC': 100})
    assert ret[0] is False


def test_percentwait_morethan100():
    # requiring 5*10 = 50mins = 3000sec
    ret = pw(dict(uris=['file:///tenminute.ogg']),
             {'status': {'time': '4800:6000'}},
             {'EF_MAXWAIT_PERC': 500})
    assert ret[0] is True

    ret = pw(dict(uris=['file:///oneminute.ogg']),
             {'status': {'time': '2000:6000'}},
             {'EF_MAXWAIT_PERC': 500})
    assert ret[0] is False
