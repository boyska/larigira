import wave


def maxwait(songs, context, conf):
    wait = int(conf.get('EF_MAXWAIT_SEC', 0))
    if wait == 0:
        return True
    if 'time' not in context['status']:
        return True, 'no song playing?'
    curpos, duration = map(int, context['status']['time'].split(':'))
    remaining = duration - curpos
    if remaining > wait:
        return False, 'remaining %d max allowed %d' % (remaining, wait)
    return True


def get_duration(path):
    '''get track duration in seconds'''
    if path.lower().endswith('.wav'):
        with wave.open(path, 'r') as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / rate
            return int(duration)
    try:
        import mutagen
    except ModuleNotFoundError:
        raise ImportError("mutagen not installed")

    audio = mutagen.File(path)
    if audio is None:
        return None
    return int(audio.info.length)


def percentwait(songs, context, conf, getdur=get_duration):
    '''
    Similar to maxwait, but the maximum waiting time is proportional to the
    duration of the audio we're going to add.

    This filter observe the EF_MAXWAIT_PERC variable.
    The variable must be an integer representing the percentual.
    If the variable is 0 or unset, the filter will not run.

    For example, if the currently playing track still has 1 minute to go and we
    are adding a jingle of 40seconds, then if EF_MAXWAIT_PERC==200 the audio
    will be added (40s*200% = 1m20s) while if EF_MAXWAIT_PERC==100 it will be
    filtered out.
    '''
    percentwait = int(conf.get('EF_MAXWAIT_PERC', 0))
    if percentwait == 0:
        return True
    if 'time' not in context['status']:
        return True, 'no song playing?'
    curpos, duration = map(int, context['status']['time'].split(':'))
    remaining = duration - curpos
    eventduration = 0
    for uri in songs['uris']:
        if not uri.startswith('file://'):
            return True, '%s is not a file' % uri
        path = uri[len('file://'):]  # strips file://
        songduration = getdur(path)
        if songduration is None:
            continue
        eventduration += songduration

    wait = eventduration * (percentwait/100.)
    if remaining > wait:
        return False, 'remaining %d max allowed %d' % (remaining, wait)
    return True
