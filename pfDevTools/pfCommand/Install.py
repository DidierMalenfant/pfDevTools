# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import zipfile
import tempfile
import contextlib
import pfDevTools.Utils
import pfDevTools.CoreConfig

from sys import platform
from distutils.dir_util import copy_tree


# -- Classes
class Install:
    """A tool to install a zipped up core file onto a given volume (SD card or Pocket in USB access mode)."""

    def __init__(self, arguments):
        """Constructor based on command line arguments."""

        self._zip_filename = None
        self._volume_path = None

        nb_of_arguments = len(arguments)
        if nb_of_arguments != 0:
            if nb_of_arguments == 2:
                self._volume_path = arguments[1]
                arguments = arguments[:0]
                nb_of_arguments -= 1
            else:
                self._volume_path = pfDevTools.CoreConfig.coreInstallVolumePath()

            if nb_of_arguments != 1:
                raise RuntimeError('Invalid arguments. Maybe start with `pf --help?')

            self._zip_filename = arguments[0]

            components = os.path.splitext(self._zip_filename)
            if len(components) != 2 or components[1] != '.zip':
                raise RuntimeError('Can only install zipped up core files.')

            if not os.path.exists(self._zip_filename):
                raise RuntimeError('File \'' + self._zip_filename + '\' does not exist.')

            if not os.path.exists(self._volume_path):
                raise RuntimeError(f'Volume {self._volume_path} is not mounted.')

    def _destCoresFolder(self) -> str:
        return os.path.join(self._volume_path, 'Cores')

    def _destPlatformsFolder(self) -> str:
        return os.path.join(self._volume_path, 'Platforms')

    def _deleteFile(self, filepath) -> None:
        with contextlib.suppress(FileNotFoundError):
            os.remove(filepath)

    def run(self) -> None:
        if self._volume_path is None:
            pfDevTools.Utils.shellCommand('scons -Q -s install')
            return

        # -- In a temporary folder.
        with tempfile.TemporaryDirectory() as tmp_dir:
            # -- Unzip the file.
            with zipfile.ZipFile(self._zip_filename, 'r') as zip_ref:
                zip_ref.extractall(tmp_dir)

            # -- Copy core files
            print('Copying core files...')

            core_src_folder = os.path.join(tmp_dir, 'Cores')
            core_dest_folder = self._destCoresFolder()

            if not os.path.isdir(core_src_folder):
                raise RuntimeError('Cannot find \'' + core_src_folder + '\' in the core release zip file.')

            copy_tree(core_src_folder, core_dest_folder)

            # -- Copy platform files
            print('Copying platforms files...')

            platforms_src_folder = os.path.join(tmp_dir, 'Platforms')
            platforms_dest_folder = self._destPlatformsFolder()

            if not os.path.isdir(platforms_src_folder):
                raise RuntimeError('Cannot find \'' + platforms_src_folder + '\' in the core release zip file.')

            copy_tree(platforms_src_folder, platforms_dest_folder)

    @classmethod
    def name(cls) -> str:
        return 'install'

    @classmethod
    def usage(cls) -> None:
        print(f'   install zip_file <{"dest_volume" if platform == "darwin" else "volume_path"}>        - Install core on volume.')
