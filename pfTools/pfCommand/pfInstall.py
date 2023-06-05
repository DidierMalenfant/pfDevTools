# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import zipfile
import tempfile
import contextlib

from sys import platform

from distutils.dir_util import copy_tree
from pfTools.pfUtils import pfUtils


# -- Classes
class pfInstall:
    """A tool to install a zipped up core file onto a given volume (SD card or Pocket in USB access mode)."""

    def __init__(self, arguments):
        """Constructor based on command line arguments."""

        self._zip_filename = None
        self._volume_name = None

        if len(arguments) != 0:
            if len(arguments) != 2:
                raise RuntimeError('Invalid arguments. Maybe start with `pf --help?')

            self._zip_filename = arguments[0]
            self._volume_name = arguments[1]

            components = os.path.splitext(self._zip_filename)
            if len(components) != 2 or components[1] != '.zip':
                raise RuntimeError('Can only install zipped up core files.')

            if not os.path.exists(self._zip_filename):
                raise RuntimeError('File \'' + self._zip_filename + '\' does not exist.')

    def _destVolume(self) -> str:
        if platform == "darwin":
            volume_path = os.path.join('/Volumes', self._volume_name)
        else:
            print('Installing cores is only supported on macOS right now.')

        if not os.path.exists(volume_path):
            raise RuntimeError(f'Volume {self._volume_name} is not mounted.')

        return volume_path

    def _destCoresFolder(self) -> str:
        return os.path.join(self._destVolume(), 'Cores')

    def _destPlatformsFolder(self) -> str:
        return os.path.join(self._destVolume(), 'Platforms')

    def _deleteFile(self, filepath) -> None:
        with contextlib.suppress(FileNotFoundError):
            os.remove(filepath)

    def run(self) -> None:
        if self._volume_name is None:
            pfUtils.shellCommand(['scons', '-Q', '-s', 'install'])
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
        print('   install <zip_file> <dest_volume>        - Install core on volume.')
