#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os
import sys
import codecs
try:
    import py2exe
except ImportError:
    pass
import re

here = os.path.abspath(os.path.dirname(__file__))

def get_global_str_from_file(rel_filepath, var):
    prog = re.compile(r'^{0} = ("|\')(.*?)("|\')'.format(var))
    with open(os.path.join(here, rel_filepath), 'r') as f:
        for line in f.readlines():
            res = prog.match(line)
            if res is not None:
                return str(res.group(2))

initFile = 'cherrymusicserver/__init__.py'
VERSION = get_global_str_from_file(initFile, 'VERSION')
DESCRIPTION = get_global_str_from_file(initFile, 'DESCRIPTION')

import gzip
def gzipManPages():
    localManPagePath = 'doc/man'
    for manpage in os.listdir(localManPagePath):
        #man pages end in numbers
        if manpage.endswith(tuple(map(str,range(10)))):
            manpagefn = os.path.join(localManPagePath, manpage)
            with open(manpagefn, 'rb') as manfile:
                manfilegz = gzip.open(manpagefn+'.gz', 'wb')
                manfilegz.writelines(manfile)
                manfilegz.close()

def list_files_in_dir(crawlpath, installpath, filterfunc=None, excluded_paths=None):
    all_files = []
    for dirpath, dirnames, filenames in os.walk(crawlpath):
        if excluded_paths and any(dirpath.startswith(path) for path in excluded_paths):
            continue
        files = []
        for filename in filenames:
            if filterfunc:
                if not filterfunc(filename):
                    continue
            files += [os.path.join(dirpath, filename)]
        all_files += [(os.path.join(installpath, dirpath), files)]
    return all_files

def module(foldername):
    ret = [foldername]
    for i in os.listdir(foldername):
        if i == '__pycache__':
            continue
        subfolder = os.path.join(foldername, i)
        if os.path.isdir(subfolder) and _ispackage(subfolder):
            ret += module(subfolder)
            ret += [subfolder.replace(os.sep,'.')]
    return ret

def _ispackage(foldername):
    return '__init__.py' in os.listdir(foldername)

def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()

def packagedata(pkgfolder, childpath=''):
    ret = []
    for n in os.listdir(os.path.join(pkgfolder, childpath)):
        if n == '__pycache__':
            continue
        child = os.path.join(childpath, n)
        fullchild = os.path.join(pkgfolder, child)
        if os.path.isdir(fullchild):
            if not _ispackage(fullchild):
                ret += packagedata(pkgfolder, child)
        elif os.path.isfile(fullchild):
            if not os.path.splitext(n)[1].startswith('.py'):
                ret += [child]
    return ret

#setup preparations:
gzipManPages()
pathproviderFile = os.path.join('cherrymusicserver/pathprovider.py')
shareFolder = os.path.join(
    'share', get_global_str_from_file(pathproviderFile, 'sharedFolderName')
)

# files to put in /usr/share
data_files = list_files_in_dir(
    'res',
    shareFolder,
    excluded_paths=['res/react-client/node_modules']
)

long_description = None
if 'upload' in sys.argv or 'register' in sys.argv:
    readmemd = "\n" + "\n".join([read('README.md')])
    print("converting markdown to reStucturedText for upload to pypi.")
    from urllib.request import urlopen
    from urllib.parse import quote
    import json

    url = 'http://pandoc.org/cgi-bin/trypandoc?from=markdown&to=rst&text=%s'
    urlhandler = urlopen(url % quote(readmemd))
    result = json.loads(codecs.decode(urlhandler.read(), 'utf-8'))

    long_description = result['html']
else:
    long_description = "\n" + "\n".join([read('README.md')])

setup_options = {
    'name': 'CherryMusic',
    'version': VERSION,
    'description': DESCRIPTION,
    'long_description': long_description,
    'author': 'Tom Wallroth & Tilman Boerner',
    'author_email': 'tomwallroth@gmail.com, tilman.boerner@gmx.net',
    'url': 'http://www.fomori.org/cherrymusic/',
    'license': 'GPLv3',
    'install_requires': ['CherryPy >= 3.2.2'],
    'packages': module('cherrymusicserver')+module('tinytag')+module('audiotranscode')+module('cmbootstrap')+module('backport'),
    'package_data': {
        'cherrymusicserver.database.defs': packagedata('cherrymusicserver/database/defs'),
    },
    #startup script
    'scripts': ['cherrymusic','cherrymusicd','cherrymusic-tray'],
    'classifiers': [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: CherryPy',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Multimedia',
        'Topic :: Multimedia :: Sound/Audio :: Players',
        ],
    'data_files': data_files
}

if os.name == 'nt':
    #py2exe specific
    setup_options['console'] = [
        {
            'icon_resources': [(1, 'res/favicon.ico')],
            'script':'cherrymusic'
        }
    ]

setup(**setup_options)
