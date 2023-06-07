# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import shutil
import contextlib

from pathlib import Path


# -- Classes
class pfDelete:
    """A tool to delete a core from a given volume (SD card or Pocket in USB access mode)."""

    def __init__(self, arguments):
        """Constructor based on command line arguments."""

        if len(arguments) != 2:
            raise RuntimeError('Invalid arguments. Maybe start with `pf --help?')

        self._name_of_core_to_delete: str = arguments[0]
        self._volume_name: str = arguments[1]

    def _destCoresFolder(self) -> str:
        return os.path.join('/Volumes', self._volume_name, 'Cores')

    def _destPlatformsFolder(self) -> str:
        return os.path.join('/Volumes', self._volume_name, 'Platforms')

    def _deleteFile(self, filepath) -> None:
        with contextlib.suppress(FileNotFoundError):
            os.remove(filepath)

    def run(self) -> None:
        cores_folder = self._destCoresFolder()
        core_folder = os.path.join(self._destCoresFolder(), self._name_of_core_to_delete)

        if os.path.exists(core_folder):
            print('Deleting ' + core_folder + '...')
            shutil.rmtree(core_folder, ignore_errors=True)

        hidden_core_data = os.path.join(self._destCoresFolder(), '._' + self._name_of_core_to_delete)
        if os.path.exists(hidden_core_data):
            print('Deleting ' + hidden_core_data + '...')
            self._deleteFile(hidden_core_data)

        core_name = pfDelete._coreNameFrom(self._name_of_core_to_delete)
        if core_name is None:
            raise RuntimeError('Could not figure out the core name from \'' + self._name_of_core_to_delete + ' \'.')

        for p in Path(cores_folder).rglob('*'):
            if not os.path.isdir(p):
                continue

            if pfDelete._coreNameFrom(os.path.basename(p)) == core_name:
                print('Found another implementation of the ' + core_name + ' platform, not deleting any Plaform data for this core.')
                return

        platforms_folder = self._destPlatformsFolder()
        core_name = core_name.lower()
        for p in Path(platforms_folder).rglob('*'):
            if os.path.isdir(p):
                continue

            filename = os.path.basename(p)
            if filename == core_name + '.bin':
                print('Deleting ' + str(p) + '...')
                self._deleteFile(p)
            elif filename == core_name + '.json':
                print('Deleting ' + str(p) + '...')
                self._deleteFile(p)
            elif filename == '._' + core_name + '.bin':
                print('Deleting ' + str(p) + '...')
                self._deleteFile(p)
            elif filename == '._' + core_name + '.json':
                print('Deleting ' + str(p) + '...')
                self._deleteFile(p)

    @classmethod
    def _coreNameFrom(cls, name: str) -> str:
        components = os.path.splitext(name)
        if len(components) != 2:
            return None

        return components[1][1:]

    @classmethod
    def name(cls) -> str:
        return 'delete'

    @classmethod
    def usage(cls) -> None:
        print('   delete core_name dest_volume          - Delete core on volume.')