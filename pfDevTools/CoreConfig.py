# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from typing import Dict
from sys import platform

from .Exceptions import ArgumentError

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


# -- Classes
class CoreConfig:
    """A class for openFPGA core configurations"""

    def __init__(self, config_filename: str):
        """Constructor based on config file path."""

        self.config_filename: str = config_filename
        self._platform_short_name = None

        components = os.path.splitext(self.config_filename)
        if len(components) != 2 or components[1] != '.toml':
            raise ArgumentError('Config file needs to be a toml file.')

        if not os.path.exists(self.config_filename):
            raise ArgumentError('Config file \'' + self.config_filename + '\' does not exist.')

        self.config_file_folder = os.path.dirname(self.config_filename)

        with open(self.config_filename, mode="rb") as fp:
            self._config = tomllib.load(fp)

    def _getConfigParam(self, section_name: str, param_name: str) -> str:
        section: Dict = self._config.get(section_name, None)

        if section is None:
            raise RuntimeError(f'Can\'t find section named {section_name} in config file.')

        param: str = section.get(param_name, None)
        if param is None:
            raise RuntimeError(f'Can\'t find parameter {param_name} in sectior {section_name} in config file.')

        return param

    def platformName(self) -> str:
        return self._getConfigParam('Platform', 'name')

    def platformImage(self) -> str:
        return os.path.join(self.config_file_folder, self._getConfigParam('Platform', 'image'))

    def platformShortName(self) -> str:
        if self._platform_short_name is None:
            self._platform_short_name = self._getConfigParam('Platform', 'short_name')

            for c in self._platform_short_name:
                if (c.isalnum() is False) or c.isupper():
                    raise RuntimeError('Platform short name should be lower-case and can only contain a-z, 0-9 or _.')

        return self._platform_short_name

    def platformCategory(self) -> str:
        return self._getConfigParam('Platform', 'category')

    def platformDescription(self) -> str:
        return self._getConfigParam('Platform', 'description')

    def platformInfoFile(self) -> str:
        platform_config = self._config.get('Platform', None)
        if platform_config is not None:
            info_file = platform_config.get('info', None)

            if info_file is not None:
                return os.path.expandvars(os.path.join(self.config_file_folder, info_file))

        return None

    def buildVersion(self) -> str:
        return self._getConfigParam('Build', 'version')

    def authorName(self) -> str:
        return self._getConfigParam('Author', 'name')

    def authorIcon(self) -> str:
        return os.path.join(self.config_file_folder, self._getConfigParam('Author', 'icon'))

    def authorURL(self) -> str:
        return self._getConfigParam('Author', 'url')

    def videoWidth(self) -> str:
        return self._getConfigParam('Video', 'width')

    def videoHeight(self) -> str:
        return self._getConfigParam('Video', 'height')

    def videoAspectRatioWidth(self) -> str:
        return self._getConfigParam('Video', 'aspect_w')

    def videoAspectRatioHeight(self) -> str:
        return self._getConfigParam('Video', 'aspect_h')

    def videoRotation(self) -> str:
        return self._getConfigParam('Video', 'rotation')

    def videoMirror(self) -> str:
        return self._getConfigParam('Video', 'mirror')

    def fullPlatformName(self) -> str:
        return f'{self.authorName()}.{self.platformShortName()}'

    @classmethod
    def coreInstallVolumePath(cls) -> str:
        # -- On macOS, if PF_CORE_INSTALL_VOLUME is not defined, we default to POCKET
        volume_name: str = os.environ.get('PF_CORE_INSTALL_VOLUME', "POCKET")
        if platform == "darwin":
            return os.path.join('/Volumes', volume_name)
        else:
            raise RuntimeError('PF_CORE_INSTALL_VOLUME is not defined in the environment.')
