# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pfDevTools.OpenFPGACore
import SCons.Environment


def SConsEnvironment(**kwargs):
    env = SCons.Environment.Environment(**kwargs)

    env.AddMethod(pfDevTools.OpenFPGACore.build, 'OpenFPGACore')

    return env
