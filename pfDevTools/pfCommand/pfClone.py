# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from pfDevTools.pfUtils import pfUtils
from pfDevTools.Exceptions import ArgumentError


# -- Classes
class pfClone:
    """A tool to clone the Github core template."""

    def __init__(self, arguments):
        """Constructor based on command line arguments."""

        self._tag_name: str = None
        self._url: str = 'https://github.com/DidierMalenfant/pfCoreTemplate.git'

        nb_of_arguments = len(arguments)
        if nb_of_arguments == 1 or nb_of_arguments == 3:
            self._url: str = arguments[0]
            nb_of_arguments -= 1
            arguments = arguments[1:]

        if nb_of_arguments == 0:
            self._destination_folder: str = arguments[0]
        elif nb_of_arguments == 2:
            if arguments[0].startswith('tag='):
                self._tag_name = arguments[0][4:]
            else:
                raise ArgumentError('Invalid cloning arguments. Maybe start with `pf --help?')

            self._destination_folder: str = arguments[1]
        else:
            raise ArgumentError('Invalid arguments. Maybe start with `pf --help?')

    def run(self) -> None:
        if pfUtils.commandExists('git') is False:
            raise RuntimeError('You must have git installed on your machine to continue.')

        repo_folder = os.path.join(self._destination_folder, 'pfCoreTemplate')
        if os.path.exists(repo_folder):
            pfUtils.deleteFolder(repo_folder, force_delete=True)

        print('Cloning core template in \'' + repo_folder + '\'.')

        command_line = 'git clone --depth 1 '

        if self._tag_name is not None:
            command_line += f'--branch {self._tag_name} '

        command_line += self._url

        pfUtils.shellCommand(command_line, from_dir=self._destination_folder, silent_mode=True)

        git_folder = os.path.join(repo_folder, '.git')
        if os.path.exists(git_folder):
            pfUtils.deleteFolder(git_folder, force_delete=True)

    @classmethod
    def name(cls) -> str:
        return 'clone'

    @classmethod
    def usage(cls) -> None:
        print('   clone <url> <tag=name> dest_folder    - Clone repo at url, optionally at a given tag/branch.')
        print('                                           (url defaults to pfCoreTemplate\'s repo if missing).')
