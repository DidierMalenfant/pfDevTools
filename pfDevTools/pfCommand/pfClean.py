# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pfDevTools.pfUtils import pfUtils


# -- Classes
class pfClean:
    """A tool to clean the local project."""

    def __init__(self, arguments):
        """Constructor based on command line arguments."""

        if len(arguments) != 0:
            raise RuntimeError('Invalid arguments. Maybe start with `pf --help?')

    def run(self) -> None:
        pfUtils.shellCommand('scons -c -Q -s')

    @classmethod
    def name(cls) -> str:
        return 'clean'

    @classmethod
    def usage(cls) -> None:
        print('   clean                                 - Clean the local project.')
