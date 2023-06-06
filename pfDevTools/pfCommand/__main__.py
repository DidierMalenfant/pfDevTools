# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import traceback

from .pfCommand import pfCommand
from pfDevTools.Exceptions import ArgumentError

# -- This enables more debugging information for exceptions.
_debug_on: bool = False


def main():
    global _debug_on

    try:
        if '--debug' in sys.argv:
            print('Enabling debugging information.')
            _debug_on = True

        # -- Remove the first argument (which is the script filename)
        pfCommand(sys.argv[1:]).main()
    except ArgumentError as e:
        error_string = str(e)

        if len(error_string) != 0:
            print(e)

        sys.exit(1)
    except Exception as e:
        if _debug_on is True:
            print(traceback.format_exc())
        else:
            error_string = str(e)

            if len(error_string) != 0:
                print(e)

        sys.exit(1)
    except KeyboardInterrupt:
        print('Execution interrupted by user.')
        sys.exit(1)


if __name__ == '__main__':
    main()
