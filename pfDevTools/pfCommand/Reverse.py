# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os


# -- Classes
class Reverse:
    """A tool to reverse the bitstream of an rbf file for an Analog Pocket core."""

    def __init__(self, arguments):
        """Constructor based on command line arguments."""

        if len(arguments) != 2:
            raise RuntimeError('Invalid arguments. Maybe start with `pf --help?')

        self._rbf_filename: str = arguments[0]
        self._rbf_r_filename: str = arguments[1]

        components = os.path.splitext(self._rbf_filename)
        if len(components) != 2 or components[1] != '.rbf':
            raise RuntimeError('Can only reverse .rbf files.')

        if not os.path.exists(self._rbf_filename):
            raise RuntimeError('File \'' + self._rbf_filename + '\' does not exist.')

    def run(self) -> None:
        print('Reading \'' + self._rbf_filename + '\'.')
        input_file = open(self._rbf_filename, 'rb')
        input_data = input_file.read()
        input_file.close()

        reversed_data = []
        print('Reversing ' + str(len(input_data)) + ' bytes.')
        for byte in input_data:
            reversed_byte = ((byte & 1) << 7) | ((byte & 2) << 5) | ((byte & 4) << 3) | ((byte & 8) << 1) | ((byte & 16) >> 1) | ((byte & 32) >> 3) | ((byte & 64) >> 5) | ((byte & 128) >> 7)
            reversed_data.append(reversed_byte)

        print('Writing \'' + self._rbf_r_filename + '\'.')
        output_file = open(self._rbf_r_filename, 'wb')
        output_file.write(bytearray(reversed_data))
        output_file.close()

    @classmethod
    def name(cls) -> str:
        return 'reverse'

    @classmethod
    def usage(cls) -> None:
        print('   reverse src_filename dest_filename    - Reverse a bitstream file.')
