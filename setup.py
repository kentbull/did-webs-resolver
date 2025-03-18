#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
$ python setup.py register sdist upload

First Time register project on pypi
https://pypi.org/manage/projects/


Pypi Release
$ pip3 install twine

$ python3 setup.py sdist
$ twine upload dist/keri-0.0.1.tar.gz

Create release git:
$ git tag -a v0.4.2 -m "bump version"
$ git push --tags
$ git checkout -b release_0.4.2
$ git push --set-upstream origin release_0.4.2
$ git checkout master

Best practices for setup.py and requirements.txt
https://caremad.io/posts/2013/07/setup-vs-requirement/
"""

from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages, setup

setup(
    name='dkr',
    version='0.0.7',  # also change in src/did-webs-resolver/__init__.py
    license='Apache Software License 2.0',
    description='did:webs DID Method Resolver',
    long_description="did:webs DID Method Resolver.",
    author='Philip S. Feairheller',
    author_email='pfeairheller@gmail.com',
    url='https://github.com/hyperledger-labs/did-webs-resolver',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
    project_urls={
        'Documentation': 'https://kara.readthedocs.io/',
        'Changelog': 'https://kara.readthedocs.io/en/latest/changelog.html',
        'Issue Tracker': 'https://github.com/WebOfTrust/kara/issues',
    },
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires='>=3.12.2',
    install_requires=[
                        'aiohttp==3.10.11',
                        'lmdb>=1.4.1',
                        'pysodium>=0.7.17',
                        'blake3>=0.4.1',
                        'msgpack>=1.0.8',
                        'cbor2>=5.6.2',
                        'multidict>=6.0.5',
                        'ordered-set>=4.1.0',
                        'keri>=1.2.4',
                        'hio>=0.6.14',
                        'multicommand>=1.0.0',
                        'jsonschema>=4.21.1',
                        'falcon>=3.1.3',
                        'hjson>=3.1.0',
                        'PyYaml>=6.0.1',
                        'apispec>=6.6.0',
                        'mnemonic>=0.21',
                        'PrettyTable>=3.10.0',
                        'http_sfv>=0.9.9',
                        'cryptography==44.0.1',
                        'requests>=2.28',
                        'simplejson>=3.17.0'
    ],
    extras_require={
    },
    tests_require=[
        'coverage>=7.4.4',
        'pytest>=8.1.1',
        'pytest-timeout>=2.3.1'
    ],
    setup_requires=[
    ],
    entry_points={
        'console_scripts': [
            'dkr = dkr.app.cli.dkr:main',
        ]
    },
)
