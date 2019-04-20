
from setuptools import setup

setup(name='vcsromclient',
      version='0.1.1',
      description='Dump atari2600 roms',
      url='',
      author='Koen van Vliet',
      author_email='8by8mail@gmail.com',
      license='MIT',
      packages=['vcsromclient'],
      scripts=['romclient.py'],
      entry_points={
            'console_scripts': ['romclient=romclient:main']},
      zip_safe=False,
)