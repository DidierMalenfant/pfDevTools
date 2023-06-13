# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pfDevTools.Utils


# -- Classes
class Make:
    """A tool to make the local project."""

    def __init__(self, arguments):
        """Constructor based on command line arguments."""

        if len(arguments) != 0:
            raise RuntimeError('Invalid arguments. Maybe start with `pf --help?')

    def run(self) -> None:
        pfDevTools.Utils.shellCommand('scons -Q -s')

    @classmethod
    def name(cls) -> str:
        return 'make'

    @classmethod
    def usage(cls) -> None:
        print('   make                                  - Make the local project.')
