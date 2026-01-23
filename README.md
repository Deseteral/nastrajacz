# nastrajacz

A simple configuration manager CLI tool for managing dotfiles and system configurations.

nastrajacz helps you version control your configuration files by organizing them into **fragments** (logical groups like `nvim`, `git`, `zsh`) and syncing them between your system and a repository.

## Key Concepts

- **Fragment**: A configuration group (e.g., `nvim`, `git`, `zsh`). Each fragment contains one or more targets.
- **Target**: A file or directory to manage within a fragment.
- **Fetch**: Copy configuration files from your system into the repository.
- **Apply**: Copy configuration files from the repository to your system.

## Requirements

- Python 3.11 or higher

## Installation

Clone the repository and add the `bin` directory to your PATH:

```bash
export PATH="$PATH:/path/to/nastrajacz/bin"
nastrajacz --help
```

## Configuration

Create a `fragments.toml` file in the root of your configuration repository. This file defines which files and directories to manage.

### Basic Example

```toml
[git]
targets = [
    { src = "~/.gitconfig" },
    { src = "~/.gitignore_global" },
]

[zsh]
targets = [
    { src = "~/.zshrc" },
    { src = "~/.zprofile" },
]
```

### Using Subdirectories

Use the `dir` option to organize files into subdirectories within a fragment:

```toml
[nvim]
targets = [
    { src = "~/.config/nvim", dir = "config" },
    { src = "~/.local/share/nvim/site", dir = "local" },
]
```

This stores files under `fragments/nvim/config/` and `fragments/nvim/local/` respectively.

### Target Options

| Option | Required | Description                                                           |
| ------ | -------- | --------------------------------------------------------------------- |
| `src`  | Yes      | Path to the file or directory on your system. Supports `~` expansion. |
| `dir`  | No       | Subdirectory within the fragment to store the target.                 |

## Usage

All commands must be run from the directory containing `fragments.toml`.

### Fetch Configuration

Copy files from your system to the repository:

```bash
# Fetch all fragments
nastrajacz --fetch

# Fetch specific fragments
nastrajacz --fetch --select nvim,git
```

### Apply Configuration

Copy files from the repository to your system:

```bash
# Apply all fragments
nastrajacz --apply

# Apply specific fragments
nastrajacz --apply --select nvim,git
```

### List Fragments

Display all fragments defined in the configuration:

```bash
nastrajacz --list
```

### Command Reference

| Command                | Description                                      |
| ---------------------- | ------------------------------------------------ |
| `--fetch`              | Fetch configuration from system to repository.   |
| `--apply`              | Apply configuration from repository to system.   |
| `--list`               | List all available fragments.                    |
| `--select <fragments>` | Comma-separated list of fragments to operate on. |
| `--help`               | Show help message.                               |

## Directory Structure

After fetching, your repository will have this structure:

```
your-config-repo/
├── fragments.toml
└── fragments/
    ├── git/
    │   ├── .gitconfig
    │   └── .gitignore_global
    ├── nvim/
    │   └── config/
    │       └── nvim/
    │           └── init.lua
    └── zsh/
        ├── .zshrc
        └── .zprofile
```

## Example Workflow

1. Create a new repository for your configurations.
2. Create a `fragments.toml` file defining your fragments and targets.
3. Run `nastrajacz --fetch` to copy your current configuration into the repository.
4. Commit and push to version control.
5. On a new machine, clone your repository and run `nastrajacz --apply`.

## Development

This project is managed by `uv`. For more information refer to [`uv` documentation](https://docs.astral.sh/uv/).

To run tests execute:

```sh
uv run pytest -s tests/ -v
```

## License

This project is licensed under the [MIT license](LICENSE).
