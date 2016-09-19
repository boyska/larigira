'''
This component will look for files to be removed. There are some assumptions:
    * Only files in $TMPDIR are removed. Please remember that larigira has its
      own specific TMPDIR
    * MPD URIs are parsed, and only file:/// is supported
'''
import os
import logging
import mpd


class UnusedCleaner:
    def __init__(self, conf):
        self.conf = conf
        self.waiting_removal_files = set()
        self.log = logging.getLogger(self.__class__.__name__)

    def _get_mpd(self):
        mpd_client = mpd.MPDClient(use_unicode=True)
        mpd_client.connect(self.conf['MPD_HOST'], self.conf['MPD_PORT'])
        return mpd_client

    def watch(self, uri):
        '''
        adds fpath to the list of "watched" file

        as soon as it leaves the mpc playlist, it is removed
        '''
        if not uri.startswith('file:///'):
            return  # not a file URI
        fpath = uri[len('file://'):]
        if not os.path.exists(fpath):
            self.log.warning('a path that does not exist is being monitored')
        self.waiting_removal_files.add(fpath)

    def check_playlist(self):
        '''check playlist + internal watchlist to see what can be removed'''
        mpd = self._get_mpd()
        files_in_playlist = {song['file'] for song in mpd.playlistid()
                             if song['file'].startswith('/')}
        for fpath in self.waiting_removal_files - files_in_playlist:
            # we can remove it!
            self.log.debug('removing unused: {}'.format(fpath))
            self.waiting_removal_files.remove(fpath)
            if os.path.exists(fpath):
                os.unlink(fpath)
