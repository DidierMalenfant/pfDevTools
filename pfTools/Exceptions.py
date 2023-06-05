# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

class ArgumentError(Exception):
    """Error caused when command line arguments have something wrong in them."""
    pass


class DependencyError(Exception):
    """Error caused when a dependency cannot be resolved."""
    pass
