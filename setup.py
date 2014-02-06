"""
Copyright (c) 2014 William H. Bell

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from distutils.core import setup
from setuptools import setup

classifiers = ['Development Status :: 3 - Alpha',
               'Operating System :: POSIX :: Linux',
               'License :: OSI Approved :: MIT License',
               'Intended Audience :: Developers',
               'Programming Language :: Python :: 2.6',
               'Programming Language :: Python :: 2.7',
               'Topic :: Software Development',
               'Topic :: Home Automation',
               'Topic :: System :: Hardware']

setup(
    name='RpiScratchIO',
    version='0.1.4',
    author='W. H. Bell',
    author_email='whbqcd1@gmail.com',
    packages=['RpiScratchIO'],
    scripts=['bin/RpiScratchIO'],
    url='http://pypi.python.org/pypi/RpiScratchIO/',
    license='MIT',
    description='Easy expansion of Raspberry Pi I/O within Scratch',
    long_description=open('README.txt').read(),
    keywords='Raspberry Pi GPIO Scratch',
    classifiers=classifiers,
    install_requires=[
        "scratchpy == 0.1.0",
        "spidev == 2.0",
        "RPi.GPIO >= 0.5.4",
    ],
)
