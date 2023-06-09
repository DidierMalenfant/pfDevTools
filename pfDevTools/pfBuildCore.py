# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import shutil
import pfDevTools

from typing import List
from pathlib import Path


# -- Classes
class pfBuildCore:
    """A Scons action to build on openFPGA core."""

    @classmethod
    def _cloneRepo(cls, target, source, env):
        command_line: List[str] = []

        url = env.get('PF_CORE_TEMPLATE_REPO_URL', None)
        if url is not None:
            command_line.append(url)

        tag = env.get('PF_CORE_TEMPLATE_REPO_TAG', None)
        if tag is not None:
            command_line.append(f'tag={tag}')

        command_line.append(env['PF_BUILD_FOLDER'])

        pfDevTools.pfClone(command_line).run()

    @classmethod
    def _updateQsfFile(cls, target, source, env):
        core_fpga_folder = env['PF_CORE_FPGA_FOLDER']
        core_verilog_files = [str(Path(str(f)).relative_to(core_fpga_folder)) for f in source]

        try:
            # -- Let's find out how many CPU cores the docker container is set up with
            result = pfDevTools.pfUtils.shellCommand(f'docker run --platform linux/amd64 -t --rm {env["PF_DOCKER_IMAGE"]} grep --count ^processor /proc/cpuinfo',
                                                     silent_mode=True, capture_output=True)
        except RuntimeError:
            raise RuntimeError("Cannot start docker container. Are you sure the docker engine is running?")

        pfDevTools.pfQfs([str(source[0]), str(target[0]), f'cpus={"max" if len(result) != 1 else result[0]}'] + core_verilog_files[1:]).run()

    @classmethod
    def _installCore(cls, target, source, env):
        pfDevTools.pfInstall([str(source[0])]).run()
        pfDevTools.pfEject([]).run()

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

                    env.Command(dest_path, src_path, pfBuildCore._copyFile)

        return dest_verilog_files

    @classmethod
    def _addExtraFiles(cls, env, path: str, dest_verilog_folder: str, extra_files: List[str] = []) -> List[str]:
        extra_dest_files: List[str] = []

        for file in extra_files:
            dest_path = os.path.join(dest_verilog_folder, Path(file).relative_to(path))
            extra_dest_files.append(dest_path)

            env.Command(dest_path, file, pfBuildCore._copyFile)

        return extra_dest_files

    @classmethod
    def _compileBitStream(cls, target, source, env):
        pfDevTools.pfUtils.shellCommand(f'docker run --platform linux/amd64 -t --rm -v {os.path.realpath(env["PF_CORE_FPGA_FOLDER"])}:/build {env["PF_DOCKER_IMAGE"]} quartus_sh --flow compile pf_core')

    @classmethod
    def _packageCore(cls, target, source, env):
        build_process: pfDevTools.pfPackage = pfDevTools.pfPackage([env['PF_CORE_CONFIG_FILE'], env['PF_CORE_BITSTREAM_FILE'], env['PF_BUILD_FOLDER']])
        print('Building core...')
        build_process.run()

    @classmethod
    def build(cls, env, config_file: str, extra_files: List[str] = []):
        pfDevTools.pfUtils.requireCommand('docker')

        env.SetDefault(PF_DOCKER_IMAGE='didiermalenfant/quartus:22.1-apple-silicon')

        if env.get('PF_SRC_FOLDER', None) is None:
            env.SetDefault(PF_SRC_FOLDER=Path(config_file).parent)

        src_folder: str = env['PF_SRC_FOLDER']

        env.SetDefault(PF_BUILD_FOLDER='_build')
        build_folder: str = env['PF_BUILD_FOLDER']

        env.Replace(PF_CORE_CONFIG_FILE=config_file)

        core_template_folder: str = os.path.join(build_folder, 'pfCoreTemplate')

        core_fpga_folder: str = os.path.join(core_template_folder, 'src', 'fpga')
        env.Replace(PF_CORE_FPGA_FOLDER=core_fpga_folder)

        core_input_qsf_file = os.path.join(core_fpga_folder, 'ap_core.qsf')
        core_output_qsf_file = os.path.join(core_fpga_folder, 'pf_core.qsf')

        core_output_bitstream_file = os.path.join(core_fpga_folder, 'output_files', 'pf_core.rbf')
        env.Replace(PF_CORE_BITSTREAM_FILE=core_output_bitstream_file)

        dest_verilog_folder: str = os.path.join(core_fpga_folder, 'core')

        env.Command(core_input_qsf_file, '', pfBuildCore._cloneRepo)

        dest_verilog_files: List[str] = pfBuildCore._searchSourceFiles(env, src_folder, dest_verilog_folder)
        extra_dest_files: List[str] = pfBuildCore._addExtraFiles(env, src_folder, dest_verilog_folder, extra_files)

        env.Command(core_output_qsf_file, [core_input_qsf_file] + dest_verilog_files, pfBuildCore._updateQsfFile)

        env.Command(core_output_bitstream_file, [core_output_qsf_file] + dest_verilog_files + extra_dest_files, pfBuildCore._compileBitStream)

        build_process: pfDevTools.pfPackage = pfDevTools.pfPackage([config_file, core_output_bitstream_file, build_folder])
        packaged_core = os.path.join(build_folder, build_process.packagedFilename())
        p = env.Command(packaged_core, build_process.dependencies(), pfBuildCore._packageCore)

        env.Default(packaged_core)
        env.Clean(packaged_core, build_folder)

        install_command = env.Command(None, packaged_core, pfBuildCore._installCore)
        env.Alias('install', install_command)

        return p
