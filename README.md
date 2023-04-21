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
    - [Projects](#projects)
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

        pip install --user ark-<version_number>-py3-none-any.whl

2. Check that Ark is installed:

        ark --help

## Usage

### Projects

The `projects` command group manages project operations.

Subcommands:

- `run`: Run a Project playbook.
  - `project_name`: The name of the project.
  - `playbook_file` (optional): The playbook file to run.
  - `--rotate-artifacts`: Number of artifacts to keep (default: 7).
  - `--limit`: Limit the playbook execution to a specific group or host (default: "").
  - `--extra-vars`: Pass additional variables as key-value pairs (default: "").
  - `-v`, `--verbosity`: Increase the verbosity of the output (default: 0).
- `report`: Display the last x reports for a given project.
  - `project_name`: The name of the project.
  - `-l`, `--last`: Display the last x reports (default: None).
- `lint`: Lint Project playbooks using ansible-lint.
  - `project_name`: The name of the project.
  - `playbook_file` (optional): The playbook file to lint.
  - `-v`, `--verbosity`: Increase the verbosity of the output (default: 0).

### Facts

The `facts` command group manages Ansible Facts operations.

Subcommands:

- `collect`: Collect facts from the specified directory.
  - `--directory`: Directory to search for facts (default: `config.PROJECTS_DIR`).
- `query`: Query facts for a specific host.
  - `hostname`: The name of the host to query.
  - `fact-key` (optional): The fact key to filter by.
  - `--page`: Page the output.
- `find`: Find all hosts with a given key, value pair.
  - `fact_key`: The fact key to search for.
  - `fact_value`: The fact value to match.
  - `--page`: Page the output.
- `remove`: Remove a host entry from the database.
  - `hostname`: The name of the host to remove.
- `list_hosts`: List all hosts in the database.
  - `--page`: Page the output.

### Inventory

The `inventory` command group manages Ansible Inventory operations.

Subcommands:

- `host-groups`: Display all groups a host is a member of.
  - `target_project`: The target project containing the inventory.
  - `target_host`: The target host to display the groups for.
- `list-members`: Display all hosts in a group or all groups and their members if no group is specified.
  - `target_project`: The target project containing the inventory.
  - `target_group` (optional): The target group to display the members for.
- `check-dns`: Check if all hosts in the inventory have a valid DNS entry.
  - `target_project`: The target project containing the inventory.
  - `--dns-servers`: DNS servers to use for checking (default: None).
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
  - `project_name` (optional): The name of the project to remove cron jobs from.
  - `--force`: Skip the confirmation prompt.

## Settings

Ark can be configured using environment variables. You can use a `.env` file in the project's directory to store these variables. Environment variables outside of the dotenv file can also be used to override the settings in the dotenv file.

Here are the environment variables you can set to configure Ark:

- `ARK_PROJECTS_DIR`: Set the projects directory (default: current working directory).
- `ARK_DB_URL`: Configure the database URL (default: SQLite database located in the `PROJECTS_DIR`).
- `ARK_CONSOLE_LOG_LEVEL`: Set the console log level (default: "WARNING").
- `ARK_FILE_LOG_LEVEL`: Set the file log level (default: "INFO").
- `ARK_ENCODING`: Configure the encoding used by Ark (default: "utf-8").
- `ARK_DNS_SERVERS`: Configure the DNS servers used in the `check-dns` command (default: "1.1.1.1,8.8.8.8").
- `ARK_TABLE_FORMAT`: Set the table format for displaying output (default: "psql").

To create a `.env` file in the project's directory, you can use a text editor and add the environment variables like this:

```ini
ARK_PROJECTS_DIR=/path/to/projects
ARK_DB_URL=sqlite:///path/to/database.db
ARK_CONSOLE_LOG_LEVEL=WARNING
ARK_FILE_LOG_LEVEL=INFO
ARK_ENCODING=utf-8
ARK_DNS_SERVERS=1.1.1.1,8.8.8.8
ARK_TABLE_FORMAT=psql
```

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

```ini
ARK_CONSOLE_LOG_LEVEL=INFO
ARK_FILE_LOG_LEVEL=DEBUG
```

With these settings, Ark will output "INFO" level logs to the console and "DEBUG" level logs to the log file. If you want to disable file logging, simply don't set a `log_dir` value when calling the `init_logging` function or remove the `ARK_FILE_LOG_LEVEL` variable from your environment.

## Disclaimer

- **Use at your own risk!** I am not responsible for any data loss or other issues that may occur.
- Ark is still in **Alpha** and will likely have bugs and other issues. Please [report](#issues) any issues you encounter.
- Ark is **Not Supported by or Affiliated** with [Ansible](https://github.com/ansible/ansible) or [Ansible Runner](https://github.com/ansible/ansible-runner).

## Issues

If you encounter any issues, please [Report Issues](https://gitgub.com/Get-Tony/ark/issues) on GitHub.

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
