#!/usr/bin/env python
from distutils.core import setup

import os, subprocess, glob, gzip
from distutils.dep_util import newer
from distutils.log import info
from distutils.cmd import Command
from distutils.command.build import build as _build
from distutils.command.install_data import install_data as _install_data
from distutils.command.install import install as _install

class build_trans(Command):
    description = 'Compile .po files into .mo files'

    user_options = []

    def initialize_options(self): pass
    def finalize_options(self): pass

    def run(self):
        PO_DIR = 'data/po'
        for po in glob.glob(os.path.join(PO_DIR,'*.po')):
            lang = os.path.basename(po[:-3])
            mo = os.path.join('build', 'locale', lang, 'LC_MESSAGES', 'arandr.mo')

            directory = os.path.dirname(mo)
            print mo, directory
            if not os.path.exists(directory):
                info('creating %s'%directory)
                os.makedirs(directory)

            if newer(po, mo):
                cmd = ['msgfmt', '-o', mo, po]
                info('compiling %s -> %s' % (po, mo))
                if not self.dry_run:
                    subprocess.check_call(cmd)

class build_man(Command):
    description = 'Compress man page'

    user_options = []

    def initialize_options(self): pass
    def finalize_options(self): pass

    def run(self):
        gzip.open('build/arandr.1.gz', 'w', 9).write(open('data/arandr.1').read())

class build(_build):
    sub_commands = _build.sub_commands + [('build_trans', None), ('build_man', None)]
    def run(self):
        _build.run(self)

class install_data(_install_data):
    def run(self):
        for lang in os.listdir('build/locale/'):
            lang_dir = os.path.join('share', 'locale', lang, 'LC_MESSAGES')
            lang_file = os.path.join('build', 'locale', lang, 'LC_MESSAGES', 'arandr.mo')
            self.data_files.append((lang_dir, [lang_file]))

        _install_data.run(self)

setup(name = "arandr",
	version = "0.1.2",
	description = u"Screen layout editor for xrandr 1.2 (Another XRandR gui)",
	author = u"chrysn",
	author_email = "chrysn@fsfe.org",
	packages = ['screenlayout'],
	license = u'GNU GPL 3',
	package_data = {
		'screenlayout': [
			'data/gpl-3.txt',
			],
		},
        cmdclass = {
            'build_trans': build_trans,
            'build_man': build_man,
            'build': build,
            'install_data': install_data,
            },
        data_files = [
            ('share/applications', ['data/arandr.desktop']),
            ('share/man/man1', ['build/arandr.1.gz']),
            ],
        scripts = ['arandr'],
)
