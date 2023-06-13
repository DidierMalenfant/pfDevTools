# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import getopt
import pfDevTools.Utils
import pfDevTools.Git

from semver import Version
from pathlib import Path

from pfDevTools.__about__ import __version__
from pfDevTools.Exceptions import ArgumentError

from .Clean import Clean
from .Clone import Clone
from .Convert import Convert
from .Delete import Delete
from .DryRun import DryRun
from .Eject import Eject
from .Install import Install
from .Make import Make
from .Package import Package
from .Qfs import Qfs
from .Reverse import Reverse


# -- Classes
class pfCommand:
    """The pf command line tool for Project Freedom."""

    def __init__(self, args):
        """Constructor based on command line arguments."""

        try:
            self._commands = [Clean, Clone, Convert, Delete, DryRun, Eject, Install, Make, Package, Qfs, Reverse]

            # -- Gather the arguments
            opts, arguments = getopt.getopt(args, 'dhv', ['debug', 'help', 'version'])

            for o, a in opts:
                if o in ('-d', '--debug'):
                    # -- We ignore this argument because it was already dealt with in the calling main() code.
                    continue
                elif o in ('-h', '--help'):
                    self.printUsage()
                    sys.exit(0)
                elif o in ('-v', '--version'):
                    pfCommand.printVersion()
                    sys.exit(0)

            if len(arguments) == 0:
                raise ArgumentError('Invalid arguments. Maybe start with `pf --help?')

            self._command_found = None
            for command in self._commands:
                if command.name() == arguments[0]:
                    self._command_found = command
                    break

            if self._command_found is None:
                raise ArgumentError(f'Unknown command \'{arguments[0]}\'. Maybe start with `pf --help?')

            self._arguments = arguments[1:]

        except getopt.GetoptError:
            print('Unknown option. Maybe start with `pf --help?')
            sys.exit(0)

    def main(self) -> None:
        self._command_found(self._arguments).run()

        pfCommand.checkForUpdates()

    def printUsage(self) -> None:
        pfCommand.printVersion()
        print('')
        print('usage: pf <options> command <arguments>')
        print('')
        print('The following options are supported:')
        print('')
        print('   --help/-h                             - Show a help message.')
        print('   --version/-v                          - Display the app\'s version.')
        print('   --debug/-d                            - Enable extra debugging information.')
        print('')
        print('Supported commands are:')

        for command in self._commands:
            command.usage()

        print('')

    @classmethod
    def printVersion(cls) -> None:
        print('👾 pf-dev-tools v' + __version__ + ' 👾')

        pfCommand.checkForUpdates()

    @classmethod
    def checkForUpdates(cls, force_check=False):
        try:
            file_path = pfDevTools.Paths.appUpdateCheckFile()
            if not force_check and not pfDevTools.Utils.fileOlderThan(file_path, time_in_seconds=(24 * 60 * 60)):
                return

            latest_version = pfDevTools.Git('github.com/DidierMalenfant/pfDevTools').getLatestVersion()
            if latest_version is None:
                return

            os.makedirs(Path(file_path).parent, exist_ok=True)

            if os.path.exists(file_path):
                os.remove(file_path)

            with open(file_path, 'w') as out_file:
                out_file.write('check')

            if latest_version > Version.parse(__version__):
                warning = '‼️' if sys.platform == "darwin" else '!!'
                print(f'{warning}  Version v{str(latest_version)} is available for pf-dev-tools. You have v{__version__} {warning}')
                print('Please run \'pip install pf-dev-tools --upgrade\' to upgrade.')
        except Exception:
            pass
