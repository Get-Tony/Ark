# Ark: Streamline Your Ansible Workflow

Ark is an intuitive command-line tool designed to simplify the management of multiple Ansible Runner projects. With Ark, you can Store and Query an Ansible Facts Database, display Ansible Runner result reports, schedule tasks, and more.

## Table of Contents

- [Ark: Streamline Your Ansible Workflow](#ark-streamline-your-ansible-workflow)
  - [Table of Contents](#table-of-contents)
  - [Documentation](#documentation)
  - [Requirements](#requirements)
  - [Features](#features)
    - [Commands](#commands)
    - [Settings](#settings)
    - [Database](#database)
    - [Logging](#logging)
  - [Build and Installation](#build-and-installation)
    - [Installing from Wheel](#installing-from-wheel)
    - [Build with Poetry](#build-with-poetry)
    - [Makefile (for Development)](#makefile-for-development)
  - [Disclaimer](#disclaimer)
  - [Contributing](#contributing)
  - [Code of Conduct](#code-of-conduct)
  - [Security Policy](#security-policy)
  - [License](#license)

## Documentation

The Ark package documentation is available at <https://get-tony.github.io/Ark>. It provides detailed information on the Ark package modules.

## Requirements

See the [pyproject.toml](./pyproject.toml) file for the full list of requirements.

- Python 3.9 or higher

## Features

### Commands

See the [Ark Documentation](#documentation) for detailed information.

- `run`: Run Ansible playbooks.
- `report`: Generate reports based on Ansible Runner data.
- `lint`: Lint Ansible playbooks.
- `facts`: Gather facts from Ansible Runner data.
- `inventory`: Manage Ansible inventories.
- `cron`: Schedule tasks.

### Settings

Ark can be configured using environment variables. You can use a `.env` file in the project's directory to store these variables. Environment variables outside of the dotenv file can also be used to override the settings in the dotenv file.

Here are the environment variables you can set to configure Ark:

- `ARK_PROJECTS_DIR`: Set the projects directory (default: current working directory).
- `ARK_CONSOLE_LOG_LEVEL`: Set the console log level (default: "WARNING").
- `ARK_FILE_LOG_LEVEL`: Set the file log level (default: "INFO").
- `ARK_ENCODING`: Configure the encoding used by Ark (default: "utf-8").
- `ARK_DNS_SERVERS`: Configure the DNS servers used in the `check-dns` command (default: "8.8.8.8" [Google Public DNS](https://developers.google.com/speed/public-dns/)).
- `ARK_TABLE_FORMAT`: Set the table format for displaying output (default: "psql").

To create a `.env` file in the project's directory, you can use a text editor and add the environment variables like this:

    ARK_PROJECTS_DIR=/path/to/projects
    ARK_CONSOLE_LOG_LEVEL=WARNING
    ARK_FILE_LOG_LEVEL=INFO
    ARK_ENCODING=utf-8
    ARK_DNS_SERVERS=<ip_of_dns_server1>,<ip_of_dns_server2>,<ip_of_dns_server3>

Save the file as .env in the project's directory. The environment variables will be automatically loaded when running Ark. To override any of these settings, simply set an environment variable with the same name outside of the dotenv file.

More table formats can be found in the [tabulate](https://pypi.org/project/tabulate/) documentation.

### Database

Ark uses [SQLAlchemy](https://www.sqlalchemy.org/) and [SQLModel](https://sqlmodel.tiangolo.com/) for ORM and session management.
The database is located in the `ARK_PROJECTS_DIR` by default. You can configure the database URL using the `ARK_DB_URL` environment variable. See the [Settings](#settings) section for more information.

### Logging

Ark utilizes Python's built-in logging module, allowing for flexible and customizable logging behavior. By default, console logging is set to "WARNING" level, and file logging is set to "INFO" level. You can adjust the log levels by setting the `ARK_CONSOLE_LOG_LEVEL` and ARK_FILE_LOG_LEVEL environment variables.

The `log_conf.py` file in the Ark package contains the `init_logging` function, which is responsible for initializing the logging configuration. This function sets up console and file handlers, log formatters, and log levels based on the provided parameters or environment variables.

To customize the logging behavior, you can modify the following environment variables in your `.env` file or set them as global environment variables:

`ARK_CONSOLE_LOG_LEVEL`: Set the console log level (default: "WARNING").
`ARK_FILE_LOG_LEVEL`: Set the file log level (default: "INFO").

Example of a `.env` file with finer logging settings:

    ARK_CONSOLE_LOG_LEVEL=INFO
    ARK_FILE_LOG_LEVEL=DEBUG

With these settings, Ark will output "INFO" level logs to the console and "DEBUG" level logs to the log file. If you want to disable file logging, simply don't set a `log_dir` value when calling the `init_logging` function or remove the `ARK_FILE_LOG_LEVEL` variable from your environment.

## Build and Installation

Pre-built wheels are available on the [Releases](https://github.com/Get-Tony/Ark/releases) page.

### Installing from Wheel

 1. Install the wheel file:

        python3 -m pip install --user ark-<version_number>-py3-none-any.whl

 2. Ensure the `~/.local/bin` directory is in your `$PATH` to access Ark. If it is not already added, you can do so by adding the following line to your `.bashrc` file:

            export PATH="$HOME/.local/bin:$PATH"

      To add this line to your `.bashrc` file, you can run the following command:

            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

      After adding the line, you need to reload your `.bashrc` file to apply the changes:

            source ~/.bashrc

 3. Verify the installation:

            ark --help

### Build with Poetry

1. Clone the repository:

        git clone https://github.com/Get-Tony/Ark.git

2. Change to the cloned directory:

        cd Ark

3. Install Poetry:

        pip install poetry

4. Install the required packages using Poetry:

        poetry install

5. Activate the Poetry virtual environment:

        poetry shell

6. Build Ark:

        poetry build

The wheel file will be located in the `dist` directory. See the [Installing from Wheel](#installing-from-wheel) section for installation instructions.

### Makefile (for Development)

This section outlines the usage of the Makefile, which helps automate various tasks for building, linting, and managing Ark source code.

The `make` command is used to process`Makefile`'s and is available for most Unix-based systems, such as Linux and macOS.

Targets:

- `help`: Displays the list of available targets.
- `lint-python`: Runs Python linters (black, ruff, mypy, and pylint).
- `lint-ansible`: Runs Ansible lint on all YAML files.
- `clean`: Removes cache objects.
- `check-version`: Checks version definition consistency.
- `set-version`: Sets the Ark version.
- `build`: Builds the Ark package.
- `install`: Installs Ark in development mode.
- `docs`: Builds the documentation.

To run any of the targets, use the make command followed by the target name. For example:

      make lint-python

This will run the Python linters on the project

---

[Back to top](#ark-streamline-your-ansible-workflow)

## Disclaimer

- ***Use at your own risk!*** I am not responsible for any data loss or other damages that may occur from using Ark.
- Ark is ***Not Supported by or Affiliated*** with [Ansible](https://github.com/ansible/ansible) or [Ansible Runner](https://github.com/ansible/ansible-runner).
- Ark is still in ***Alpha*** and will likely have bugs and other issues.
  Please ***report any issues*** you encounter [Here](https://github.com/Get-Tony/ark/issues).

## [Contributing](./CONTRIBUTING.md)

If you would like to contribute to this project, please read the [Contributing](./CONTRIBUTING.md) guide.

## [Code of Conduct](./CODE_OF_CONDUCT.md)

Please read our [Code of Conduct](./CODE_OF_CONDUCT.md) to understand the guidelines for participating in this project.

## [Security Policy](./SECURITY.md)

For information on reporting vulnerabilities, please read the [Security Policy](./SECURITY.md).

## [License](./LICENSE)

Ark is released under the [GPLv3 License](./LICENSE).
