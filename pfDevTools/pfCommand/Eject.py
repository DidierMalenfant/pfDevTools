# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import pfDevTools
import pfDevTools.Utils
import pfDevTools.CoreConfig

from sys import platform


# -- Classes
class Eject:
    """A tool to eject given volume (SD card or Pocket in USB access mode)."""

    def __init__(self, arguments):
        """Constructor based on command line arguments."""

        nb_of_arguments = len(arguments)
        if nb_of_arguments == 0:
            self._volume_path = pfDevTools.CoreConfig.coreInstallVolumePath()
        elif nb_of_arguments == 1:
            self._volume_path = arguments[0]
        else:
            raise RuntimeError('Invalid arguments. Maybe start with `pf --help?')

    def run(self) -> None:
        if not os.path.exists(self._volume_path):
            raise RuntimeError(f'Volume {self._volume_path} is not mounted.')

        if platform == "darwin":
            print(f'Ejecting {self._volume_path}.')
            pfDevTools.Utils.shellCommand(f'diskutil eject {self._volume_path}')
        else:
            print('Ejecting volumes is only supported on macOS right now.')

    @classmethod
    def name(cls) -> str:
        return 'eject'

    @classmethod
    def usage(cls) -> None:
        print('   eject <dest_volume>                   - Eject volume.')
