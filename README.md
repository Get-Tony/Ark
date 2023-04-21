# Ark

Ark is a command-line tool for managing multiple Ansible Runner projects.

## Table of Contents

- [Ark](#ark)
  - [Table of Contents](#table-of-contents)
  - [Requirements](#requirements)
  - [Build and Installation](#build-and-installation)
    - [Build with Poetry](#build-with-poetry)
    - [Installing a Release](#installing-a-release)
  - [Warnings](#warnings)
  - [Tips and Hints](#tips-and-hints)
  - [License](#license)
  - [Code of Conduct](#code-of-conduct)
  - [Contributing](#contributing)
  - [Security Policy](#security-policy)

## Requirements

- Python 3.9.2 or later

See the [pyproject.toml](./pyproject.toml) file for the full list of requirements.

## Build and Installation

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

### Installing a Release

1. Build Ark using the [Poetry](#build-with-poetry) instructions above. The build will create a wheel file in the `dist` directory. Alternatively, you can download a pre-built release, if currently available, from the [Releases](https://github.com/Get-Tony/Ark/releases) page.

2. Use pip to install the wheel file:

        pip install ark-<RELEASE_VERSION>-py3-none-any.whl

## Warnings

- **Ark is not officially supported** by [Ansible](https://github.com/ansible/ansible) or [Ansible Runner](https://github.com/ansible/ansible-runner). Use at your own risk!
- Use at your own risk! I am not responsible for any data loss or other issues that may occur.

## Tips and Hints

- Define the Ark environment variable `ARK_PROJECTS_DIR` to define the projects directory.
- Ark uses an SQLite database by default. You can configure the database URL using the `ARK_DB_URL` environment variable.

## [License](./LICENSE)

Ark is released under the [GPLv3 License](./LICENSE).

## [Code of Conduct](./CODE_OF_CONDUCT.md)

Please read our [Code of Conduct](./CODE_OF_CONDUCT.md) to understand the guidelines for participating in this project.

## [Contributing](./CONTRIBUTING.md)

If you would like to contribute to this project, please read the [Contributing](./CONTRIBUTING.md) guide.

## [Security Policy](./SECURITY.md)

For information on reporting vulnerabilities, please read the [Security Policy](./SECURITY.md).

---
[Back to top](#table-of-contents)
