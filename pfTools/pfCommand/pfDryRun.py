# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pfTools.pfUtils import pfUtils


# -- Classes
class pfDryRun:
    """A tool to clean the local project."""

    def __init__(self, arguments):
        """Constructor based on command line arguments."""

        if len(arguments) != 0:
            raise RuntimeError('Invalid arguments. Maybe start with `pf --help?')

    def run(self) -> None:
        pfUtils.shellCommand(['scons', '--dry-run', '--tree=all', '--debug=explain'])

    @classmethod
    def name(cls) -> str:
        return 'dryrun'

    @classmethod
    def usage(cls) -> None:
        print('   dryrun                                - Simulate building the local project.')
