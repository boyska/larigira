import sys
import os

from setuptools import setup
from setuptools.command.test import test as TestCommand


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as buf:
        return buf.read()


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(name='larigira',
      version='0.4',
      description='A radio automation based on MPD',
      long_description=read('README.rst'),
      author='boyska',
      author_email='piuttosto@logorroici.org',
      license='AGPL',
      packages=['larigira', 'larigira.dbadmin'],
      install_requires=[
          'pyxdg',
          'gevent',
          'flask-bootstrap',
          'python-mpd2',
          'wtforms',
          'Flask-WTF',
          'flask==0.11',
          'pytimeparse',
          'tinydb'
      ],
      tests_require=['pytest', 'pytest-timeout'],
      cmdclass={'test': PyTest},
      zip_safe=False,
      include_package_data=True,
      entry_points={
          'console_scripts': ['larigira=larigira.larigira:main',
                              'larigira-timegen=larigira.timegen:main',
                              'larigira-audiogen=larigira.audiogen:main',
                              'larigira-dbmanage=larigira.event_manage:main'],
          'larigira.audiogenerators': [
              'mpd = larigira.audiogen_mpdrandom:generate_by_artist',
              'static = larigira.audiogen_static:generate',
              'randomdir = larigira.audiogen_randomdir:generate',
              'mostrecent = larigira.audiogen_mostrecent:generate',
              'script = larigira.audiogen_script:generate',
          ],
          'larigira.timegenerators': [
              'frequency = larigira.timegen_every:FrequencyAlarm',
              'single = larigira.timegen_every:SingleAlarm',
          ],
          'larigira.timeform_create': [
              'single = larigira.timeform_single:SingleAlarmForm',
              'frequency = larigira.timeform_frequency:FrequencyAlarmForm',
          ],
          'larigira.timeform_receive': [
              'single = larigira.timeform_single:singlealarm_receive',
              'frequency = larigira.timeform_frequency:frequencyalarm_receive',
          ],
          'larigira.audioform_create': [
              'static = larigira.audioform_static:StaticAudioForm',
              'script = larigira.audioform_script:ScriptAudioForm',
              'randomdir = larigira.audioform_randomdir:Form',
              'mostrecent = larigira.audioform_mostrecent:AudioForm',
          ],
          'larigira.audioform_receive': [
              'static = larigira.audioform_static:staticaudio_receive',
              'script = larigira.audioform_script:scriptaudio_receive',
              'randomdir = larigira.audioform_randomdir:receive',
              'mostrecent = larigira.audioform_mostrecent:audio_receive',
          ],
      },
      classifiers=[
          "License :: OSI Approved :: GNU Affero General Public License v3",
          "Programming Language :: Python :: 3",
      ]
      )
