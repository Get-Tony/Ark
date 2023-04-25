# Ark: Streamline Your Ansible Workflow

Ark is an intuitive command-line tool designed to simplify the management of multiple Ansible Runner projects. With Ark, you can effortlessly run playbooks, organize inventories, schedule tasks, and more.

## Table of Contents

- [Ark: Streamline Your Ansible Workflow](#ark-streamline-your-ansible-workflow)
  - [Table of Contents](#table-of-contents)
  - [Requirements](#requirements)
  - [Build and Installation](#build-and-installation)
    - [Build with Poetry](#build-with-poetry)
    - [Installing from Wheel](#installing-from-wheel)
  - [Usage](#usage)
    - [Run](#run)
    - [Report](#report)
    - [Lint](#lint)
    - [Facts](#facts)
    - [Inventory](#inventory)
    - [Cron](#cron)
  - [Settings](#settings)
  - [Database](#database)
  - [Logging](#logging)
  - [Disclaimer](#disclaimer)
  - [Issues](#issues)
  - [License](#license)
  - [Code of Conduct](#code-of-conduct)
  - [Contributing](#contributing)
  - [Security Policy](#security-policy)

## Requirements

See the [pyproject.toml](./pyproject.toml) file for the full list of requirements.

- Python 3.9.2 or higher

## Build and Installation

Ark packages are available in the [Releases](https://github.com/Get-Tony/Ark/releases) section of the GitHub repository.

If you want to build Ark from source, see the [Build with Poetry](#build-with-poetry) section below.

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

## Usage

### Run

The `run` command group manages Ansible Runner operations.

- `run`: Run a Project playbook.
  - `project_name`: The name of the project.
  - `playbook_file` (optional): The playbook file to run.
  - `--rotate-artifacts`: Number of artifacts to keep (default: 7).
  - `--limit`: Limit the playbook execution to a specific group or host (default: "").
  - `--extra-vars`: Pass additional variables as key-value pairs (default: "").
  - `-v`, `--verbosity`: Increase the verbosity of the output (default: 0).

### Report

The `report` command group manages Ansible Runner event reports.

- `report`: Display the last x reports for a given project.
  - `project_name`: The name of the project.
  - `-l`, `--last`: Display the last x reports (default: None).

### Lint

The `lint` command group manages Ansible linting.

- `lint`: Lint Project playbooks using ansible-lint.
  - `project_name`: The name of the project.
  - `playbook_file` (optional): The playbook file to lint.
  - `-v`, `--verbosity`: Increase the verbosity of the output (default: 0).

### Facts

The `facts` command group manages Ansible Facts operations.

Subcommands:

- `collect`: Collect facts from the specified directory.
  - `--project_name`: Directory to search for facts (default: `config.PROJECTS_DIR`).
- `query`: Query facts for a specific host.
  - `fqdn`: The name of the host to query.
  - `fact-key` (optional): The fact key to filter by.
  - `--fuzzy`: Fuzzy search the fact key.
  - `--page`: Page the output.
- `find`: Find all hosts with a given key, value pair.
  - `fact_key`: The fact key to search for.
  - `fact_value`: The fact value to match.
  - `--fuzzy`: Fuzzy search the fact key.
  - `--page`: Page the output.
- `remove`: Remove a host entry from the database.
  - `fqdn`: The name of the host to remove.
- `show-hosts`: List all hosts in the database.
  - `--page`: Page the output.

### Inventory

The `inventory` command group manages Ansible Inventory operations.

Subcommands:

- `host-groups`: List all groups a host is a member of.
  - `project_name`: The project containing the inventory.
  - `inventory_name`: The host to display the groups for.
- `list-hosts`: List all hosts in a group or all groups and their members if no group is specified.
  - `project_name`: The target project containing the inventory.
  - `group_name` (optional): The target group to display the members for.
- `check-dns`: Check if all hosts in the inventory have a valid DNS entry.
  - `project_name`: The target project containing the inventory.
  - `--dns-server`: DNS server to use for checking (default: None). **Can be specified multiple times**
  - `--timeout`: Timeout for DNS query (default: 5).
  - `--outfile`: Output file to save results (default: None).

### Cron

The `cron` command group manages scheduled Ansible Runner tasks.

Subcommands:

- `add`: Add a new cron job.
  - `project_name`: The name of the project.
  - `playbook`: The playbook to run.
  - `--loop`: The frequency of the cron job (choices: hourly, daily; default: hourly).
  - `--hourly_minute`: The minute to run hourly cron jobs (0-59; default: 30).
  - `--daily_hour`: The hour to run daily cron jobs (0-23; default: 4).
- `list`: List all Ark-managed cron jobs.
- `remove`: Remove any Ark-managed cron jobs matching a given pattern.
  - `pattern`: The pattern to match cron jobs.
  - `--force`: Skip the confirmation prompt.
- `wipe`: Remove all Ark-managed cron jobs.
  - `project_name` (optional): Specify a project to remove only its cron jobs.
  - `--force`: Skip the confirmation prompt.

## Settings

Ark can be configured using environment variables. You can use a `.env` file in the project's directory to store these variables. Environment variables outside of the dotenv file can also be used to override the settings in the dotenv file.

Here are the environment variables you can set to configure Ark:

- `ARK_PROJECTS_DIR`: Set the projects directory (default: current working directory).
- `ARK_CONSOLE_LOG_LEVEL`: Set the console log level (default: "WARNING").
- `ARK_FILE_LOG_LEVEL`: Set the file log level (default: "INFO").
- `ARK_ENCODING`: Configure the encoding used by Ark (default: "utf-8").
- `ARK_DNS_SERVERS`: Configure the DNS servers used in the `check-dns` command (default: "1.1.1.1,8.8.8.8").
- `ARK_TABLE_FORMAT`: Set the table format for displaying output (default: "psql").

To create a `.env` file in the project's directory, you can use a text editor and add the environment variables like this:

    ARK_PROJECTS_DIR=/path/to/projects
    ARK_CONSOLE_LOG_LEVEL=WARNING
    ARK_FILE_LOG_LEVEL=INFO
    ARK_ENCODING=utf-8
    ARK_DNS_SERVERS=1.1.1.1,8.8.8.8

Save the file as .env in the project's directory. The environment variables will be automatically loaded when running Ark. To override any of these settings, simply set an environment variable with the same name outside of the dotenv file.

More table formats can be found in the [tabulate](https://pypi.org/project/tabulate/) documentation.

## Database

Ark uses [SQLAlchemy](https://www.sqlalchemy.org/) and [SQLModel](https://sqlmodel.tiangolo.com/) for ORM and session management.
The database is located in the `PROJECTS_DIR` by default. You can configure the database URL using the `ARK_DB_URL` environment variable. See the [Settings](#settings) section for more information.

## Logging

Ark utilizes Python's built-in logging module, allowing for flexible and customizable logging behavior. By default, console logging is set to "WARNING" level, and file logging is set to "INFO" level. You can adjust the log levels by setting the `ARK_CONSOLE_LOG_LEVEL` and ARK_FILE_LOG_LEVEL environment variables.

The `log_conf.py` file in the Ark package contains the `init_logging` function, which is responsible for initializing the logging configuration. This function sets up console and file handlers, log formatters, and log levels based on the provided parameters or environment variables.

To customize the logging behavior, you can modify the following environment variables in your .env file or set them in your environment:

`ARK_CONSOLE_LOG_LEVEL`: Set the console log level (default: "WARNING").
`ARK_FILE_LOG_LEVEL`: Set the file log level (default: "INFO").

Example of a `.env` file with custom logging settings:

    ARK_CONSOLE_LOG_LEVEL=WARNING
    ARK_FILE_LOG_LEVEL=DEBUG

With these settings, Ark will output "INFO" level logs to the console and "DEBUG" level logs to the log file. If you want to disable file logging, simply don't set a `log_dir` value when calling the `init_logging` function or remove the `ARK_FILE_LOG_LEVEL` variable from your environment.

## Disclaimer

- **Use at your own risk!** I am not responsible for any data loss or other issues that may occur.
- Ark is still in **Alpha** and will likely have bugs and other issues. Please [report](#issues) any issues you encounter.
- Ark is **Not Supported by or Affiliated** with [Ansible](https://github.com/ansible/ansible) or [Ansible Runner](https://github.com/ansible/ansible-runner).

## Issues

If you encounter any issues, please [Report Issues](https://github.com/Get-Tony/ark/issues) on GitHub.

## [License](./LICENSE)

Ark is released under the [GPLv3 License](./LICENSE).

## [Code of Conduct](./CODE_OF_CONDUCT.md)

Please read our [Code of Conduct](./CODE_OF_CONDUCT.md) to understand the guidelines for participating in this project.

## [Contributing](./CONTRIBUTING.md)

If you would like to contribute to this project, please read the [Contributing](./CONTRIBUTING.md) guide.

## [Security Policy](./SECURITY.md)

For information on reporting vulnerabilities, please read the [Security Policy](./SECURITY.md).

---
[Back to Table of Contents](#table-of-contents)
