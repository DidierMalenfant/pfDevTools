# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
import os
import shutil
import errno
import stat
import time

from typing import List


# -- Classes
class Utils:
    @classmethod
    def _handleRemoveReadonly(cls, func, path, exc):
        excvalue = exc[1]
        if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # -- 0777
            func(path)
        else:
            raise

    @classmethod
    def shellCommand(cls, command_and_args: str, from_dir: str = '.', silent_mode=False, env=None, capture_output=False) -> List[str]:
        try:
            merged_env = None
            if env is not None:
                merged_env = dict()
                merged_env.update(os.environ)
                merged_env.update(env)

            output: List[str] = []

            process = subprocess.Popen(command_and_args.split(' '), cwd=from_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=merged_env)
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
            Utils.shellCommand(f'{"where" if os.name == "nt" else "which"} {command}', silent_mode=True)
        except Exception:
            return False

        return True

    @classmethod
    def requireCommand(cls, command: str):
        if not Utils.commandExists(command):
            raise RuntimeError('❌ Cannot find command \'' + command + '\'.')

    @classmethod
    def deleteFolder(cls, folder: str, force_delete: bool = False):
        if os.path.exists(folder):
            if force_delete is True:
                ignore_errors = False
                on_error = Utils._handleRemoveReadonly
            else:
                ignore_errors = True
                on_error = None

            shutil.rmtree(folder, ignore_errors=ignore_errors, onerror=on_error)

    @classmethod
    def fileOlderThan(cls, path: str, time_in_seconds: int):
        if not os.path.exists(path):
            return True

        return (time.time() - os.path.getmtime(path)) > time_in_seconds
