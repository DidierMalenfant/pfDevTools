# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from typing import List
from enum import Enum

from pfDevTools.Exceptions import ArgumentError


# -- Classes
class EditingState(Enum):
    BEFORE_EDIT = 1
    DURING_EDIT = 2
    AFTER_EDIT = 3


class Qfs:
    """A tool to edit Quartus project files."""

    def __init__(self, arguments):
        """Constructor based on command line arguments."""

        if len(arguments) < 3:
            raise RuntimeError('Invalid arguments. Maybe start with `pf --help?')

        self._input_qsf_file: str = arguments[0]
        if not self._input_qsf_file.endswith('.qsf'):
            raise ArgumentError('Invalid input project file type for pf qsf.')

        if not os.path.exists(self._input_qsf_file):
            raise RuntimeError('File \'' + self._input_qsf_file + '\' does not exist.')

        self._output_qsf_file: str = arguments[1]
        if not self._output_qsf_file.endswith('.qsf'):
            raise ArgumentError('Invalid output project file type for pf qsf.')

        arguments = arguments[2:]

        self._number_of_cpus: int = 0
        if arguments[0].startswith('cpus='):
            value = arguments[0][5:]
            if value == 'max':
                self._number_of_cpus = os.cpu_count()
            else:
                self._number_of_cpus = int(value)

            arguments = arguments[1:]

        self._verilog_files: List[str] = arguments

    def _writeAdditions(self, dest_file, editing_wrappers: List[str]) -> None:
        dest_file.write(editing_wrappers[0])
        dest_file.write('# ---------------------------\n')

        if self._number_of_cpus != 0:
            dest_file.write('set_global_assignment -name NUM_PARALLEL_PROCESSORS ' + str(self._number_of_cpus) + '\n')

        for file in self._verilog_files:
            dest_file.write('set_global_assignment -name ')

            if file.endswith('.v'):
                dest_file.write('VERILOG_FILE ')
            elif file.endswith('.sv'):
                dest_file.write('SYSTEMVERILOG_FILE ')
            else:
                raise ArgumentError('Unknown file type for \'' + file + '\'.')

            dest_file.write(file.replace('\\', '/') + '\n')

        dest_file.write('\n' + editing_wrappers[1])

    def run(self) -> None:
        print('Updating QSF file...')

        editing_wrappers: List[str] = ['# Additions made by pf command\n',
                                       '# End of additions made by pf command\n']

        src_file = open(self._input_qsf_file, 'r')
        dest_file = open(self._output_qsf_file, 'w')

        editing_state = EditingState.BEFORE_EDIT
        last_line = None

        for line in src_file.readlines():
            last_line = line

            match editing_state:
                case EditingState.BEFORE_EDIT:
                    if line == editing_wrappers[0]:
                        self._writeAdditions(dest_file, editing_wrappers)

                        editing_state = EditingState.DURING_EDIT
                    else:
                        dest_file.write(line)
                case EditingState.DURING_EDIT:
                    if line == editing_wrappers[1]:
                        editing_state = EditingState.AFTER_EDIT
                case EditingState.AFTER_EDIT:
                    dest_file.write(line)

        if editing_state == EditingState.BEFORE_EDIT:
            if not last_line.endswith('\n'):
                dest_file.write('\n')

            if last_line != '\n':
                dest_file.write('\n')

            self._writeAdditions(dest_file, editing_wrappers)

        src_file.close()
        dest_file.close()

    @classmethod
    def name(cls) -> str:
        return 'qfs'

    @classmethod
    def usage(cls) -> None:
        print('   qfs qsf_in qsf_out <cpus=num> files   - Add files and set number of cpu for the project.')
        print('                                           (if num is \'max\' then all CPU cores will be used).')
