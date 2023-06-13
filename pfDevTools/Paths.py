# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import tempfile


class Paths:
    """Various paths used by pfDevTools."""

    @classmethod
    def tempFolder(cls):
        return os.path.join(tempfile.gettempdir(), 'io.projectfreedom')

    @classmethod
    def appUpdateCheckFile(cls):
        return os.path.join(Paths.tempFolder(), 'app-update-check')
