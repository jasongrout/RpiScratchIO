from distutils.core import setup

setup(
    name='RpiScratchIO',
    version='0.1.0',
    author='W. H. Bell',
    author_email='whbqcd1@gmail.com',
    packages=['RpiScratchIO'],
    scripts=['bin/RpiScratchIO'],
    url='http://pypi.python.org/pypi/RpiScratchIO/',
    license='LICENSE.txt',
    description='Easy expansion of Raspberry Pi I/O within Scratch',
    long_description=open('README.txt').read(),
    install_requires=[
        "scratchpi == 0.1.0",
        "spidev == 2.0",
        "RPi.GPIO >= 0.5.4",
    ],
)
