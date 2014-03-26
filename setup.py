from sys import version
from pip.req import parse_requirements
from setuptools import setup

install_reqs = [str(x.req) for x in parse_requirements('requirements.txt')]

setup(name='twistedschedule',
      version='0.1',
      description='TwistedSchedule v0.1',
      author='Gabe Fierro',
      author_email='fierro@eecs.berkeley.edu',
      url='https://github.com/SoftwareDefinedBuildings/TwistedSchedule/',
      license='TBD',
      packages = ['twistedschedule'],
      install_requires=install_reqs
)
