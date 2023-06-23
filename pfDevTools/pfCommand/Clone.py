# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import pfDevTools.Utils
import pfDevTools.Git

from pfDevTools.Exceptions import ArgumentError


# -- Classes
class Clone:
    """A tool to clone the Github core template."""

    def __init__(self, arguments):
        """Constructor based on command line arguments."""

        self._destination_folder: str = None
        self._tag_name: str = None
        self._url: str = 'github.com/DidierMalenfant/pfCoreTemplate'

        nb_of_arguments = len(arguments)
        while nb_of_arguments:
            if nb_of_arguments == 1:
                self._destination_folder: str = arguments[0]
            elif arguments[0].startswith('tag='):
                self._tag_name = arguments[0][4:]
            else:
                self._url: str = arguments[0]

            nb_of_arguments -= 1
            arguments = arguments[1:]

        if self._destination_folder is None:
            raise ArgumentError('Invalid arguments. Maybe start with `pf --help?')

    def run(self) -> None:
        repo_folder = os.path.join(self._destination_folder, 'pfCoreTemplate')
        if os.path.exists(repo_folder):
            pfDevTools.Utils.deleteFolder(repo_folder, force_delete=True)

        print('Cloning core template in \'' + repo_folder + '\'.')

        pfDevTools.Git(self._url).cloneIn(repo_folder, self._tag_name)

        git_folder = os.path.join(repo_folder, '.git')
        if os.path.exists(git_folder):
            pfDevTools.Utils.deleteFolder(git_folder, force_delete=True)

    @classmethod
    def name(cls) -> str:
        return 'clone'

    @classmethod
    def usage(cls) -> None:
        print('   clone <url> <tag=name> dest_folder    - Clone repo at url, optionally at a given tag/branch.')
        print('                                           (url defaults to pfCoreTemplate\'s repo if missing).')
