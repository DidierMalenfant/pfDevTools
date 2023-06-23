# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import shutil
import pfDevTools

from typing import List
from pathlib import Path
from distutils.dir_util import copy_tree


# -- Classes
class OpenFPGACore:
    """A SCons action to build on openFPGA core."""

    @classmethod
    def _cloneRepo(cls, target, source, env):
        command_line: List[str] = []

        url = env.get('PF_CORE_TEMPLATE_REPO_URL', None)
        if url is not None:
            command_line.append(url)

        tag = env.get('PF_CORE_TEMPLATE_REPO_TAG', None)
        if tag is not None:
            command_line.append(f'tag={tag}')

        repo_folder = env['PF_CORE_TEMPLATE_FOLDER']
        command_line.append(repo_folder)

        if os.path.exists(repo_folder):
            pfDevTools.Utils.deleteFolder(repo_folder, force_delete=True)

        pfDevTools.Clone(command_line).run()

    @classmethod
    def _copyRepo(cls, target, source, env):
        src_folder = os.path.expanduser(env['PF_CORE_TEMPLATE_REPO_FOLDER'])
        dest_folder = env['PF_CORE_TEMPLATE_FOLDER']

        if not os.path.exists(src_folder) or not os.path.isdir(src_folder):
            raise RuntimeError(f'Cannot find \'{src_folder}\' to copy core tmeplate repo from.')

        print(f'Copying core template repo from \'{src_folder}\'.')

        if os.path.exists(dest_folder):
            pfDevTools.Utils.deleteFolder(dest_folder, force_delete=True)

        copy_tree(src_folder, dest_folder)

    @classmethod
    def _runDockerCommand(cls, image: str, command: str, build_folder: str = None, quiet: bool = True):
        try:
            pfDevTools.Utils.requireCommand('docker')

            if not OpenFPGACore._dockerIsRunning():
                raise RuntimeError('Docker engine does not seem to be running.')

            if not OpenFPGACore._dockerHasImage(image):
                print(f'Docker needs to download image \'{image}\'. This may take a while...')
                OpenFPGACore._getNumberOfDockerCPUs(image)

            command_line: str = 'docker run --platform linux/amd64 -t --rm '

            if build_folder is not None:
                command_line += f'-v {build_folder}:/build '

            command_line += image + ' ' + command

            return pfDevTools.Utils.shellCommand(command_line, silent_mode=quiet, capture_output=True)
        except Exception as e:
            error_string = str(e)

            if len(error_string) != 0:
                print(e)

            sys.exit(1)

    @classmethod
    def _dockerIsRunning(cls) -> bool:
        try:
            pfDevTools.Utils.shellCommand('docker ps', silent_mode=True, capture_output=False)
        except RuntimeError:
            return False

        return True

    @classmethod
    def _dockerHasImage(cls, image: str) -> bool:
        result = pfDevTools.Utils.shellCommand('docker images', silent_mode=True, capture_output=True)

        image_info = image.split(':')
        if len(image_info) == 2:
            looking_for = f'{image_info[0]}   {image_info[1]}'
            for line in result:
                if line.startswith(looking_for):
                    return True

        return False

    @classmethod
    def _getNumberOfDockerCPUs(cls, image: str, quiet: bool = True) -> int:
        number_of_cpus: int = 1

        result = OpenFPGACore._runDockerCommand(image, 'grep --count ^processor /proc/cpuinfo', quiet=quiet)
        if len(result) == 1:
            num_cpus_found: int = int(result[0])
            if num_cpus_found != 0:
                number_of_cpus = num_cpus_found

        return number_of_cpus

    @classmethod
    def _updateQsfFile(cls, target, source, env):
        core_fpga_folder = env['PF_CORE_FPGA_FOLDER']
        core_verilog_files = [str(Path(str(f)).relative_to(core_fpga_folder)) for f in source]
        number_of_cpus: int = OpenFPGACore._getNumberOfDockerCPUs(env['PF_DOCKER_IMAGE'])
        pfDevTools.Qfs([str(source[0]), str(target[0]), f'cpus={number_of_cpus}'] + core_verilog_files[1:]).run()

    @classmethod
    def _installCore(cls, target, source, env):
        pfDevTools.Install([str(source[0])]).run()
        pfDevTools.Eject([]).run()

    @classmethod
    def _copyFile(cls, target, source, env):
        source_file = str(source[0])
        target_file = str(target[0])
        parent_dest_dir = Path(target_file).parent
        os.makedirs(parent_dest_dir, exist_ok=True)
        shutil.copyfile(source_file, target_file)

    @classmethod
    def _searchSourceFiles(cls, env, path: str, dest_verilog_folder: str) -> List[str]:
        dest_verilog_files: List[str] = []

        for root, dirs, files in os.walk(path, topdown=False):
            for file in files:
                if file.endswith('.sv') or file.endswith('.v'):
                    src_path = os.path.join(root, file)
                    dest_path = os.path.join(dest_verilog_folder, Path(src_path).relative_to(path))
                    dest_verilog_files.append(dest_path)

                    env.Command(dest_path, src_path, OpenFPGACore._copyFile)

        return dest_verilog_files

    @classmethod
    def _addExtraFiles(cls, env, path: str, dest_verilog_folder: str, extra_files: List[str] = []) -> List[str]:
        extra_dest_files: List[str] = []

        for file in extra_files:
            dest_path = os.path.join(dest_verilog_folder, Path(file).relative_to(path))
            extra_dest_files.append(dest_path)

            env.Command(dest_path, file, OpenFPGACore._copyFile)

        return extra_dest_files

    @classmethod
    def _compileBitStream(cls, target, source, env):
        print('Compiling core bitstream...')
        OpenFPGACore._runDockerCommand(env['PF_DOCKER_IMAGE'],
                                       'quartus_sh --flow compile pf_core',
                                       build_folder=os.path.realpath(env['PF_CORE_FPGA_FOLDER']),
                                       quiet=False)

    @classmethod
    def _packageCore(cls, target, source, env):
        build_process: pfDevTools.Package = pfDevTools.Package([env['PF_CORE_CONFIG_FILE'], env['PF_CORE_BITSTREAM_FILE'], env['PF_BUILD_FOLDER']])
        print('Packaging core...')
        build_process.run()


def build(env, config_file: str, extra_files: List[str] = []):
    env.SetDefault(PF_DOCKER_IMAGE='didiermalenfant/quartus:22.1-apple-silicon')

    if env.get('PF_SRC_FOLDER', None) is None:
        env.SetDefault(PF_SRC_FOLDER=Path(config_file).parent)

    src_folder: str = env['PF_SRC_FOLDER']

    env.SetDefault(PF_BUILD_FOLDER='_build')
    build_folder: str = env['PF_BUILD_FOLDER']

    env.Replace(PF_CORE_CONFIG_FILE=config_file)

    core_template_folder: str = os.path.join(build_folder, '_core_template_repo')
    env.Replace(PF_CORE_TEMPLATE_FOLDER=core_template_folder)

    core_fpga_folder: str = os.path.join(core_template_folder, 'src', 'fpga')
    env.Replace(PF_CORE_FPGA_FOLDER=core_fpga_folder)

    core_input_qsf_file = os.path.join(core_fpga_folder, 'ap_core.qsf')
    core_output_qsf_file = os.path.join(core_fpga_folder, 'pf_core.qsf')

    core_output_bitstream_file = os.path.join(core_fpga_folder, 'output_files', 'pf_core.rbf')
    env.Replace(PF_CORE_BITSTREAM_FILE=core_output_bitstream_file)

    dest_verilog_folder: str = os.path.join(core_fpga_folder, 'core')

    if env.get('PF_CORE_TEMPLATE_REPO_FOLDER', None) is None:
        env.Command(core_input_qsf_file, '', OpenFPGACore._cloneRepo)
    else:
        env.Command(core_input_qsf_file, '', OpenFPGACore._copyRepo)

    dest_verilog_files: List[str] = OpenFPGACore._searchSourceFiles(env, src_folder, dest_verilog_folder)
    extra_dest_files: List[str] = OpenFPGACore._addExtraFiles(env, src_folder, dest_verilog_folder, extra_files)

    env.Command(core_output_qsf_file, [core_input_qsf_file] + dest_verilog_files, OpenFPGACore._updateQsfFile)
    env.Command(core_output_bitstream_file, [core_output_qsf_file] + dest_verilog_files + extra_dest_files, OpenFPGACore._compileBitStream)

    build_process: pfDevTools.Package = pfDevTools.Package([config_file, core_output_bitstream_file, build_folder])
    packaged_core = os.path.join(build_folder, build_process.packagedFilename())
    p = env.Command(packaged_core, build_process.dependencies(), OpenFPGACore._packageCore)

    env.Default(packaged_core)
    env.Clean(packaged_core, build_folder)

    install_command = env.Command(None, packaged_core, OpenFPGACore._installCore)
    env.Alias('install', install_command)

    return p
