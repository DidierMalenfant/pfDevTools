# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys

from .pfCommand.Clean import Clean
from .pfCommand.Clone import Clone
from .pfCommand.Convert import Convert
from .pfCommand.Delete import Delete
from .pfCommand.DryRun import DryRun
from .pfCommand.Eject import Eject
from .pfCommand.Install import Install
from .pfCommand.Make import Make
from .pfCommand.Package import Package
from .pfCommand.Qfs import Qfs
from .pfCommand.Reverse import Reverse

from .CoreConfig import CoreConfig
from .Git import Git
from .Paths import Paths
from .SCons import SConsEnvironment
from .Utils import Utils

from semver import Version

from .__about__ import __version__


# --- Makes sure current pfDevTools versions is supported
def requires(version: str) -> bool:
    current = Version.parse(__version__, optional_minor_and_patch=True)
    required = Version.parse(version, optional_minor_and_patch=True)

    if not (required.major == current.major) and ((current.minor > required.minor) or ((current.minor == required.minor) and (current.patch >= required.patch))) and (required.prerelease == current.prerelease):
        raise RuntimeError(f'pfDevTools v{str(current)} is not compatible with the required version v{str(required)}.')
