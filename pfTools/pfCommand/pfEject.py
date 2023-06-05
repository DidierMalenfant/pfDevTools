# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from sys import platform

from pfTools.pfUtils import pfUtils


# -- Classes
class pfEject:
    """A tool to eject given volume (SD card or Pocket in USB access mode)."""

    def __init__(self, arguments):
        """Constructor based on command line arguments."""

        if len(arguments) != 1:
            raise RuntimeError('Invalid arguments. Maybe start with `pf --help?')

        self._volume_name = arguments[0]

    def run(self) -> None:
        if platform == "darwin":
            if not os.path.exists(os.path.join('/Volumes', self._volume_name)):
                raise RuntimeError(f'Volume {self._volume_name} is not mounted.')

            print('Ejecting \'' + self._volume_name + '\'.')
            pfUtils.shellCommand(['diskutil', 'eject', self._volume_name])
        else:
            print('Ejecting volumes is only supported on macOS right now.')

    @classmethod
    def name(cls) -> str:
        return 'eject'

    @classmethod
    def usage(cls) -> None:
        print('   eject <dest_volume>                   - Eject volume.')
