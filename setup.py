#!/usr/bin/env python

from os.path import exists
from setuptools import setup



setup(name='cachey',
      version='0.1.1',
      description='Caching mindful of computation/storage costs',
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering",
    ],
      url='http://github.com/dask/cachey/',
      maintainer='Matthew Rocklin',
      maintainer_email='mrocklin@gmail.com',
      license='BSD',
      keywords='',
      packages=['cachey'],
      python_requires='>=3.6',
      install_requires=list(open('requirements.txt').read().strip().split('\n')),
      long_description=(open('README.md').read() if exists('README.md')
                        else ''),
      zip_safe=False)
