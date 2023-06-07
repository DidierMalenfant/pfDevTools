# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys

from .pfCommand.pfClone import pfClone
from .pfCommand.pfConvert import pfConvert
from .pfCommand.pfDelete import pfDelete
from .pfCommand.pfEject import pfEject
from .pfCommand.pfInstall import pfInstall
from .pfCommand.pfMake import pfMake
from .pfCommand.pfPackage import pfPackage
from .pfCommand.pfQfs import pfQfs
from .pfCommand.pfReverse import pfReverse

from .pfConfig import pfConfig
from .pfSconsEnvironment import Environment
from .pfUtils import pfUtils

from semver import Version

from .__about__ import __version__


# --- Makes sure current pfDevTools versions is supported
def requires(version: str) -> bool:
    current = Version.parse(__version__, optional_minor_and_patch=True)
    required = Version.parse(version, optional_minor_and_patch=True)

    if not (required.major == current.major) and ((current.minor > required.minor) or ((current.minor == required.minor) and (current.patch >= required.patch))) and (required.prerelease == current.prerelease):
        raise RuntimeError(f'pfDevTools v{str(current)} is not compatible with the required version v{str(required)}')
