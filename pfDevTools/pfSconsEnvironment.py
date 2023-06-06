# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pfDevTools.pfBuildCore import pfBuildCore

import SCons.Environment


def Environment(**kwargs):
    env = SCons.Environment.Environment(**kwargs)

    env.AddMethod(pfBuildCore.build, 'OpenFPGACore')

    return env
