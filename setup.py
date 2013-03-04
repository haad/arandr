#!/usr/bin/env python

# ARandR -- Another XRandR GUI
# Copyright (C) 2008 -- 2011 chrysn <chrysn@fsfe.org>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import operator
import subprocess
import glob
import gzip

import docutils.core
import docutils.writers.manpage

from distutils.core import setup
from distutils.dep_util import newer
from distutils.log import info, warn
from distutils.cmd import Command
from distutils.command.build import build as _build
from distutils.command.install_data import install_data as _install_data
from distutils.command.install import install as _install
from distutils.command.sdist import sdist as _sdist
from distutils.dir_util import remove_tree
from distutils.command.clean import clean as _clean


PO_DIR = 'data/po'
POT_FILE = os.path.join(PO_DIR, 'messages.pot')

PACKAGENAME = "arandr"
PACKAGEVERSION = "0.1.7.1"
AUTHOR = "chrysn"
AUTHOR_MAIL = "chrysn@fsfe.org"
URL = "http://christian.amsuess.com/tools/arandr/"
LICENSE = "GNU GPL 3"
DESCRIPTION = "Screen layout editor for xrandr (Another XRandR gui)"

class NoOptionCommand(Command):
    """Command that doesn't take any options"""
    user_options = []

    def initialize_options(self): pass
    def finalize_options(self): pass

class update_pot(NoOptionCommand):
    description = 'Update the .pot translation template'

    def run(self):
        all_py_files = sorted(reduce(operator.add, [[os.path.join(dn, f) for f in fs if f.endswith('.py')] for (dn,ds,fs) in os.walk('.')])) # sort to make diffs easier
        # not working around xgettext not substituting for PACKAGE everywhere in the header; it's just a template and usually worked on using tools that ignore much of it anyway
        if not self.dry_run:
            info('Creating %s' % POT_FILE)
            subprocess.check_call(['xgettext', '-LPython', '-o', POT_FILE, '--copyright-holder', AUTHOR, '--package-name', PACKAGENAME, '--package-version', PACKAGEVERSION, '--msgid-bugs-address', AUTHOR_MAIL, '--add-comments=#'] + all_py_files)

class update_po(NoOptionCommand):
    description = 'Update the .po translations from .pot translation template'

    def run(self):
        # msgmerge data/po/da.po data/po/messages.pot -U
        for po in glob.glob(os.path.join(PO_DIR, '*.po')):
            if not self.dry_run:
                info('Updating %s' % po)
                subprocess.check_call(['msgmerge', '-U', po, POT_FILE])

class build_trans(NoOptionCommand):
    description = 'Compile .po files into .mo files'

    def run(self):
        self.mkpath(os.path.join("build", "locale")) # create directory even if there are no files, otherwise install would complain
        for po in glob.glob(os.path.join(PO_DIR,'*.po')):
            lang = os.path.basename(po[:-3])
            mo = os.path.join('build', 'locale', lang, 'LC_MESSAGES', 'arandr.mo')

            directory = os.path.dirname(mo)
            self.mkpath(directory)

            if newer(po, mo):
                cmd = ['msgfmt', '-o', mo, po]
                info('compiling %s -> %s' % (po, mo))
                if not self.dry_run:
                    subprocess.check_call(cmd)

class build_man(NoOptionCommand):
    description = 'Generate and compress man page'

    def run(self):
        self.mkpath('build')

        for (sourcefile, gzfile) in [
                ('data/arandr.1.txt', os.path.join('build', 'arandr.1.gz')),
                ('data/unxrandr.1.txt', os.path.join('build', 'unxrandr.1.gz')),
                ]:

            if newer(sourcefile, gzfile):
                rst_source = open(sourcefile).read()
                manpage = docutils.core.publish_string(rst_source, writer=docutils.writers.manpage.Writer())
                info('compressing man page to %s', gzfile)

                if not self.dry_run:
                    compressed = gzip.open(gzfile, 'w', 9)
                    compressed.write(manpage)
                    compressed.close()

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

class sdist(_sdist):
    def run(self):
        warn("WARNING: Usually, arandr's source tarballs are generated from `git archive`!")
        _sdist.run(self)

class clean(_clean):
    def run(self):
        if self.all:
            dirs = ['build/locale']
            files = ['build/arandr.1.gz', 'build/unxrandr.1.gz']
            for directory in dirs:
                if os.path.exists(directory):
                    remove_tree(directory, dry_run=self.dry_run)
                else:
                    warn("%r does not exist -- can't clean it", directory)
            if not self.dry_run:
                for file in files:
                    if os.path.exists(file):
                        os.unlink(file)
                    else:
                        warn("%r does not exist -- can't clean it", file)
        _clean.run(self)


setup(name = PACKAGENAME,
    version = PACKAGEVERSION,
    description = DESCRIPTION,
    author = AUTHOR,
    author_email = AUTHOR_MAIL,
    url = URL,
    packages = ['screenlayout'],
    license = LICENSE,
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
            'sdist': sdist,
            'clean': clean,
            'update_pot': update_pot,
            'update_po': update_po,
            },
        data_files = [
            ('share/applications', ['data/arandr.desktop']), # FIXME: use desktop-file-install?
            ('share/man/man1', ['build/arandr.1.gz', 'build/unxrandr.1.gz']),
            ],
        scripts = ['arandr', 'unxrandr'],
)
