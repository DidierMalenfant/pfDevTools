# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import shutil
import zipfile
import pfDevTools

from typing import List
from pathlib import Path
from datetime import date


# -- Classes
class Package:
    """A tool to package an analog pocket core"""

    def __init__(self, arguments):
        """Constructor based on command line arguments."""

        if len(arguments) != 3:
            raise RuntimeError('Invalid arguments. Maybe start with `pf --help?')

        self._config = pfDevTools.CoreConfig(arguments[0])
        self._bitstream_file: str = arguments[1]
        self._destination_folder: str = arguments[2]
        self._core_folder = os.path.join(self._destination_folder, '_core')
        self._today = str(date.today())

    def _generateDefinitionFiles(self, cores_folder, platforms_folder) -> None:
        output_filename = os.path.join(cores_folder, 'audio.json')
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "audio": {\n')
            out_file.write('    "magic": "APF_VER_1"\n')
            out_file.write('  }\n')
            out_file.write('}\n')

        output_filename = os.path.join(cores_folder, 'data.json')
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "data": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "data_slots": []\n')
            out_file.write('  }\n')
            out_file.write('}\n')

        output_filename = os.path.join(cores_folder, 'input.json')
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "input": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "controllers": []\n')
            out_file.write('  }\n')
            out_file.write('}\n')

        output_filename = os.path.join(cores_folder, 'variants.json')
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "variants": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "variant_list": []\n')
            out_file.write('  }\n')
            out_file.write('}\n')

        output_filename = os.path.join(cores_folder, 'interact.json')
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "interact": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "variables": [],\n')
            out_file.write('    "messages": []\n')
            out_file.write('  }\n')
            out_file.write('}\n')

        output_filename = os.path.join(cores_folder, 'video.json')
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "video": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "scaler_modes": [\n')
            out_file.write('      {\n')
            out_file.write('        "width": %d,\n' % (self._config.videoWidth()))
            out_file.write('        "height": %d,\n' % (self._config.videoHeight()))
            out_file.write('        "aspect_w": %d,\n' % (self._config.videoAspectRatioWidth()))
            out_file.write('        "aspect_h": %d,\n' % (self._config.videoAspectRatioHeight()))
            out_file.write('        "rotation": %d,\n' % (self._config.videoRotation()))
            out_file.write('        "mirror": %d\n' % (self._config.videoMirror()))
            out_file.write('      }\n')
            out_file.write('    ]\n')
            out_file.write('  }\n')
            out_file.write('}\n')

        output_filename = os.path.join(platforms_folder, '%s.json' % (self._config.platformShortName()))
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "platform": {\n')
            out_file.write('    "category": "%s",\n' % (self._config.platformCategory()))
            out_file.write('    "name": "%s",\n' % (self._config.platformName()))
            out_file.write('    "year": %s,\n' % (self._today.split('-')[0]))
            out_file.write('    "manufacturer": "%s"\n' % (self._config.authorName()))
            out_file.write('  }\n')
            out_file.write('}\n')

        output_filename = os.path.join(cores_folder, 'core.json')
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "core": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "metadata": {\n')
            out_file.write('      "platform_ids": ["%s"],\n' % (self._config.platformShortName()))
            out_file.write('      "shortname": "%s",\n' % (self._config.platformShortName()))
            out_file.write('      "description": "%s",\n' % (self._config.platformDescription()))
            out_file.write('      "author": "%s",\n' % (self._config.authorName()))
            out_file.write('      "url": "%s",\n' % (self._config.authorURL()))
            out_file.write('      "version": "%s",\n' % (self._config.buildVersion()))
            out_file.write('      "date_release": "%s"\n' % (self._today))
            out_file.write('    },\n')
            out_file.write('    "framework": {\n')
            out_file.write('      "target_product": "Analogue Pocket",\n')
            out_file.write('      "version_required": "1.1",\n')
            out_file.write('      "sleep_supported": false,\n')
            out_file.write('      "dock": {\n')
            out_file.write('        "supported": true,\n')
            out_file.write('        "analog_output": false\n')
            out_file.write('      },\n')
            out_file.write('      "hardware": {\n')
            out_file.write('        "link_port": false,\n')
            out_file.write('        "cartridge_adapter": -1\n')
            out_file.write('      }\n')
            out_file.write('    },\n')
            out_file.write('    "cores": [\n')
            out_file.write('      {\n')
            out_file.write('        "name": "default",\n')
            out_file.write('        "id": 0,\n')
            out_file.write('        "filename": "%s.rbf_r"\n' % (self._config.platformShortName()))
            out_file.write('      }\n')
            out_file.write('    ]\n')
            out_file.write('  }\n')
            out_file.write('}\n')

    def _convertImages(self, cores_folder, platforms_image_folder) -> None:
        dest_bin_file = os.path.join(platforms_image_folder, '%s.bin' % (self._config.platformShortName()))
        pfDevTools.Convert([self._config.platformImage(), dest_bin_file]).run()

        dest_bin_file = os.path.join(cores_folder, 'icon.bin')
        pfDevTools.Convert([self._config.authorIcon(), dest_bin_file]).run()

    def _packageCore(self):
        packaged_filename = os.path.abspath(os.path.join(self._destination_folder, self.packagedFilename()))
        if os.path.exists(packaged_filename):
            os.remove(packaged_filename)

        with zipfile.ZipFile(packaged_filename, 'w') as myzip:
            for p in Path(self._core_folder).rglob('*'):
                if os.path.isdir(p):
                    continue

                relative_path = p.relative_to(self._core_folder)
                print('   adding \'' + str(relative_path) + '\'')
                myzip.write(p, arcname=relative_path, compress_type=zipfile.ZIP_DEFLATED)

    def dependencies(self) -> List[str]:
        deps: List[str] = [self._config.config_filename,
                           self._config.platformImage(),
                           self._config.authorIcon(),
                           self._bitstream_file]

        info_file = self._config.platformInfoFile()
        if info_file is not None:
            deps.append(info_file)

        return deps

    def packagedFilename(self) -> str:
        return '%s-%s-%s.zip' % (self._config.fullPlatformName(), self._config.buildVersion(), self._today)

    def run(self) -> None:
        # -- We delete the core build folder in case stale files are in there (for example after changing the core config file)
        if os.path.exists(self._core_folder):
            shutil.rmtree(self._core_folder)

        os.makedirs(self._core_folder)

        full_platform_name = self._config.fullPlatformName()
        cores_folder = os.path.join(self._core_folder, 'Cores', full_platform_name)
        os.makedirs(cores_folder, exist_ok=True)

        platforms_folder = os.path.join(self._core_folder, 'Platforms')
        os.makedirs(platforms_folder, exist_ok=True)

        platforms_image_folder = os.path.join(platforms_folder, '_images')
        os.makedirs(platforms_image_folder, exist_ok=True)

        print('Reversing bitstream file...')
        bitstream_dest = os.path.join(cores_folder, '%s.rbf_r' % self._config.platformShortName())
        pfDevTools.Reverse([self._bitstream_file, bitstream_dest]).run()

        print('Generating definitions files...')
        self._generateDefinitionFiles(cores_folder, platforms_folder)

        print('Converting images...')
        self._convertImages(cores_folder, platforms_image_folder)

        info_file = self._config.platformInfoFile()
        if info_file is not None:
            dest_info = os.path.join(cores_folder, 'info.txt')
            shutil.copyfile(info_file, dest_info)

        print('Packaging core...')
        self._packageCore()

    @classmethod
    def name(cls) -> str:
        return 'build'

    @classmethod
    def usage(cls) -> None:
        print('   build config_file bistream_file dest_folder')
        print('                                         - Build core according to a config_file.')
