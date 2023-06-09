# pfDevTools

[![GPL-v3.0](https://img.shields.io/github/license/DidierMalenfant/pfDevTools)](https://spdx.org/licenses/GPL-3.0-or-later.html) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pf-dev-tools.svg)](https://python.org) [![PyPI - Version](https://img.shields.io/pypi/v/pf-dev-tools.svg)](https://pypi.org/project/pf-dev-tools)

A collection of tools for [Project Freedom](https://didier.malenfant.net/ProjectFreedom/) projects.

Copyright (c) 2023-present **Didier Malenfant**.

-----

### Installation

**pfDevTools** works on **macOS**, **Linux** and **Windows**.

You can install **pfDevTools** by typing the following in a terminal window:
```console
pip install pf-dev-tools
```

See the [pre-requisites](#pre-requisites) section below for more info on installing **pfDevTools** dependencies.

### pf Command

**pfDevTools**'s main functionality is centered around the `pf` command. It provides tools used for building **openFPGA** cores and will also eventually be used to build **pfx** roms.

Usage:
```console
  pf <options> command <arguments>
```
The following options are supported:
```
  --help/-h                             - Show a help message.
  --version/-v                          - Display the app's version.
  --debug/-d                            - Enable extra debugging information.
```

#### `clean` command
```console
  pf clean
```
Cleans the local project and deletes any intermediate build files. This should be executed in the same folder as the project's `SConstruct` file.

#### `clone` command
```console
  pf clone <url> <tag=name> dest_folder
```
Clones the repo found at `url`, optionally at a given tag/branch named `name` into the folder `dest_folder`. 'url' does not need to be pre-fixed with `https://` or post-fixed with `.git`.

If `url` is missing then `github.com/DidierMalenfant/pfCoreTemplate` is used.

#### `convert` command
```console
  pf convert src_filename dest_filename
```
Converts an image to the openFGPA binary format used for core images and author icons.

#### `delete` command
```console
  pf delete core_name <dest_volume>
```
Deletes all core data (bitstream, images, icons, json files) for core named `core_name` on volume <dest_volume>.

If `dest_volume` is omitted then the command looks for the `PF_CORE_INSTALL_VOLUME` environment variable. If this is not defined either then it defaults to `/Volumes/POCKET` on **macOS** and errors out on other platforms.

If another implementation of the core is found then the Platforms files will be kepts otherwise they are deleted too.

#### `dryrun` command
```console
  pf dryrun
```
Simulate building the local project. This will give out information on what, if anything, needs to be rebuilt.

This should be executed in the same folder as the project's `SConstruct` file.

#### `eject` command
```console
  pf eject <dest_volume>
```
Ejects the volume at `dest_volume`. This command is currently only supported on **macOS**. If `dest_volume` is omitted then the command looks for the `PF_CORE_INSTALL_VOLUME` environment variable. If this is not defined either then it defaults to `/Volumes/POCKET`.

#### `install` command
```console
  pf install zip_file <dest_volume>
```
Installs the packaged core contained in `zip_file` onto volume `dest_volume`.

If `dest_volume` is omitted then the command looks for the `PF_CORE_INSTALL_VOLUME` environment variable. If this is not defined either then it defaults to `/Volumes/POCKET` on **macOS** and errors out on other platforms.

#### make command
```console
  pf make
```
Builds the local project.

This should be executed in the same folder as the project's `SConstruct` file.

#### package command                                     
```console
 pf package config_file bistream_file dest_folder
```
Packages a core into a zip file according to the content of `config_file`. The format for the configuration can be found [below](#core-config-file-format). `bistream_file` is the path to a reversed bitstream file for the core. Resulting package is written in `dest_folder`.

#### qfs command
```console
  pf qfs qsf_in qsf_out <cpus=num> files...
```
Edits a **Quartus** `qfs` project file to add files and set number of cpu for the project. Reads the `qfs` file at `qsf_in` and writes the result to `qsf_out`. `files` is a list of **Verilog** `.v` or `.sv` files, separated by spaces.

Optionally `cpus` can set the number of cpu cores that the compilation process can use. If `num` is `max` then all available **CPU** cores will be used.

#### reverse command
```console
  pf reverse src_filename dest_filename
```
Reverses the bitstream file at `src_filename` and writes it to `dest_filename`.

### Building an openFPGA core

**pfDevTools** provides an entire toolchain needed to compile **openFPGA** cores. The build systems is based on the [**SCons**](https://scons.org) software construction tool which is entirely written in **Python**.

A typical makefile is named `SConstruct` and for openFPGA projects can look as simple as this:
```python
  import pfDevTools

  # -- We need pf-dev-tools version 1.x.x but at least 1.0.5.
  pfDevTools.requires('1.0.5')

  env = pfDevTools.SConsEnvironment()
  env.OpenFPGACore('src/config.toml')
```

This will build, using `pf make`, a packaged core file based on the `toml` config [file](#core-config-file-format) and the source code found in the `src` folder.

All projects should contain at least one `core/core_top.v` file at the root of their source tree. The content of this file should be based around **Analogue**'s own `core.top.v` [file](https://github.com/open-fpga/core-template/blob/main/src/fpga/core/core_top.v) but you do not need to provide any other files or **IP** found in the [core template](https://github.com/open-fpga/core-template). Those will be automatically brought in for you during the build.

Good examples of simple core projects can be found in the examples provided as part of the [openFPGA tutorials](https://github.com/DidierMalenfant/openFPGA-tutorials).

The build environment can be customized by passing variables to the `pfDevTools.SConsEnvironment()` method call like so:
```python
  env = pfDevTools.SConsEnvironment(PF_BUILD_FOLDER='MyBuildFolder', PF_SRC_FOLDER='MySrcFolder')
```

The following variables are currently supported:

- `PF_DOCKER_IMAGE` - Name of the **Docker** image used to compile the core's bitstream. Defaults to `didiermalenfant/quartus:22.1-apple-silicon`.
- `PF_SRC_FOLDER` - Root folder for all the **Verilog** source files for the project. Defaults to the folder where the `toml` config [file]](#core-config-file-format) is located.
- `PF_BUILD_FOLDER` - Folder where intermediate build files are created. Defaults to `_build`.
- `PF_CORE_TEMPLATE_REPO_URL` - Repo url to use instead of the default core template repo at `github.com/DidierMalenfant/pfCoreTemplate`.
- `PF_CORE_TEMPLATE_REPO_TAG` - Repo tag to use to clone the core template repo.
- `PF_CORE_TEMPLATE_REPO_FOLDER` - Path to a local core template folder to copy instead of cloning a repo.

### Core config file format

Core configuration is done via a single `toml` file like this one:

```
[Platform]
name = "pfx-1"
image = "assets/pfx1-platform-image.png"
short_name = "pfx1"
category = "Fantasy"
description = "An open-source fantasy gaming console for the Analog Pocket."
info = "info.txt"

[Build]
version = "0.0.5"

[Author]
name = "dm"
icon = "assets/pfx1-core-author-icon.png"
url = "https://didier.malenfant.net/ProjectFreedom/"

[Video]
width = 400
height = 360
aspect_w = 10
aspect_h = 9
rotation = 0
mirror = 0
```

All the fields used here are similar to the ones found in **Analogue**'s own [core definition files](https://www.analogue.co/developer/docs/core-definition-files).

### Calling the build system without the pf command

In some cases, like when build is being called from inside an **IDE**, you may need to call the build system directly without using the `pf` command. You can do this by using the following equivalent commands:

- '`scons -Q --quiet`' instead of '`pf make`'.
- '`scons -Q --quiet install`' instead of '`pf install`'.
- '`scons -c -Q --quiet`' instead of '`pf clean`'.

### Pre-requisites

**pfDevTools** requires at least [Python](https://python.org) 3.10. Make sure you have a [supported version](http://didier.malenfant.net/blog/nerdy/2022/08/17/installing-python.html) of **Python** before proceeding.

It also uses the [git](https://git-scm.com) command. If you're on **macOS** and **Linux** this should come already built in on.

Finally, if you wish to build openFPGA cores, you'll need to install [Docker Desktop](https://www.docker.com/get-started/) on your machine.

Make sure the **Docker Engine** is running while building the core. If you're running on an **Apple Silicon** Mac, also make sure that the feature `Use Rosetta for x86/amd64 emulation on Apple Silicon` is enabled in `Settings->Features in development`. This setting somehow turns itself off sometimes.

### Installing Docker on Ubuntu Linux

Make sure that no other version of **Docker** are installed:
```
sudo apt-get remove docker docker-engine docker.io containerd runc
```

Add the docker repository:
```
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Install the **Docker Engine**:
```
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

In order to be able to run `docker` without `sudo`, make sure the `docker` group exists and add your user to it:
```
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

You can verify that the **Docker Engine** installation is successful by running the `hello-world` image:
```
docker run hello-world
```

### Trademarks

**openFPGA** and the **openFPGA** logo are trademarks of [**Analogue**](https://www.analogue.co/) Enterprises Ltd.
**Quartus** is a registered trademark of [**Intel**](https://intel.com/).

This project is not affiliated, associated with, sponsored or supported by neither **Analogue** nor **Intel**.

### License

**pfDevTools** is distributed under the terms of the [GPLv3.0](https://spdx.org/licenses/GPL-3.0-or-later.html) or later license.
