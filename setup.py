import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


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
      version='0.1',
      description='A radio automation based on MPD',
      author='boyska',
      author_email='piuttosto@logorroici.org',
      license='AGPL',
      packages=['larigira'],
      install_requires=[
          'gevent',
          'flask',
          'python-mpd2',
          'redis',
          'celery'
      ],
      tests_require=['pytest'],
      cmdclass={'test': PyTest},
      zip_safe=False,
      entry_points={
          'console_scripts': ['larigira=larigira.mpc:main',
                              'larigira-audiogen=larigira.audiogen:main'],
          'larigira.audiogenerators': [
              'static = larigira.audiogen_static:generate',
              'randomdir = larigira.audiogen_randomdir:generate'
          ]
      }
      )
