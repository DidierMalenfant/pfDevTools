# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
import os

from typing import List


# -- Classes
class pfUtils:
    @classmethod
    def shellCommand(cls, command_and_args: List[str], from_dir: str = '.', silent_mode=False, env=None, capture_output=False) -> List[str]:
        try:
            merged_env = None
            if env is not None:
                merged_env = dict()
                merged_env.update(os.environ)
                merged_env.update(env)

            output: List[str] = []

            process = subprocess.Popen(command_and_args, cwd=from_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=merged_env)
            if silent_mode is False or capture_output is True:
                for line in iter(process.stdout.readline, ""):
                    line = line.decode("utf-8")
                    if line == "":
                        break

                    line = line.rstrip()

                    if capture_output is True:
                        output.append(line)

                    if silent_mode is False:
                        print(line)

            if process.wait() != 0:
                raise RuntimeError

            return output
        except RuntimeError:
            raise
        except SyntaxError:
            raise
        except Exception as e:
            raise RuntimeError(str(e))

    @classmethod
    def commandExists(cls, command: str) -> bool:
        try:
            pfUtils.shellCommand(['gcm' if os.name == 'nt' else 'which', command], silent_mode=True)
        except Exception:
            return False

        return True

    @classmethod
    def requireCommand(cls, command: str):
        if not pfUtils.commandExists(command):
            raise RuntimeError('❌ Cannot find command \'' + command + '\'.')
