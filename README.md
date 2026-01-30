# nastrajacz

A simple configuration manager CLI tool for managing dotfiles and system configurations.

nastrajacz helps you version control your configuration files by organizing them into **fragments** (logical groups like `nvim`, `git`, `zsh`) and syncing them between your system and a repository.

## Key concepts

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

### Basic example

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

### Using subdirectories

Use the `dir` option to organize files into subdirectories within a fragment:

```toml
[nvim]
targets = [
    { src = "~/.config/nvim", dir = "config" },
    { src = "~/.local/share/nvim/site", dir = "local" },
]
```

This stores files under `fragments/nvim/config/` and `fragments/nvim/local/` respectively.

### Target options

| Option    | Required | Description                                                                                                 |
| --------- | -------- | ----------------------------------------------------------------------------------------------------------- |
| `src`     | Yes      | Path to the file or directory on your system. Supports `~` expansion.                                       |
| `dir`     | No       | Subdirectory within the fragment to store the target.                                                       |
| `actions` | No       | Shell commands to run before/after fetching or applying this target. See [Target actions](#target-actions). |

### Fragment actions

You can define shell commands to run before and after applying or fetching a fragment using the `actions` section:

```toml
[some_service]
targets = [
    { src = "~/.config/some_service" },
]

[some_service.actions]
before_fetch = "docker compose stop"
after_fetch = "docker compose start"
before_apply = "some_service --will-update"
after_apply = "some_service --install-updates"
```

#### Action options

| Option         | Description                                                                  |
| -------------- | ---------------------------------------------------------------------------- |
| `before_fetch` | Shell command to run before fetching. If it fails, the fragment is skipped.  |
| `after_fetch`  | Shell command to run after fetching. If it fails, only a warning is printed. |
| `before_apply` | Shell command to run before applying. If it fails, the fragment is skipped.  |
| `after_apply`  | Shell command to run after applying. If it fails, only a warning is printed. |

**Behavior:**

- Actions run in the fragment's directory (`./fragments/<fragment_name>/`).
- If `before_apply` or `before_fetch` exits with a non-zero status, the fragment is skipped entirely (no files are copied, and the corresponding `after_*` action does not run).
- If `after_apply` or `after_fetch` exits with a non-zero status, a warning is printed but other fragments continue processing.
- Empty strings are treated as undefined (no action runs).

### Target actions

In addition to fragment-level actions, you can define actions for individual targets. Target actions run before or after each specific file/directory is copied:

```toml
[nvim]
targets = [
    { src = "~/.config/nvim", actions = { before_apply = "echo 'Updating nvim config'", after_apply = "nvim --headless +PlugInstall +qa" } },
    { src = "~/.local/share/nvim/site" },
]
```

#### Target action options

| Option         | Description                                                                              |
| -------------- | ---------------------------------------------------------------------------------------- |
| `before_fetch` | Shell command to run before fetching this target. If it fails, the target is skipped.    |
| `after_fetch`  | Shell command to run after fetching this target. If it fails, only a warning is printed. |
| `before_apply` | Shell command to run before applying this target. If it fails, the target is skipped.    |
| `after_apply`  | Shell command to run after applying this target. If it fails, only a warning is printed. |

**Behavior:**

- For `--apply`: target actions run in the fragment's directory (`./fragments/<fragment_name>/`).
- For `--fetch`: target actions run in the fragments parent directory (`./fragments/`).
- If `before_apply` or `before_fetch` fails, only that specific target is skipped; other targets in the same fragment continue processing.
- If `after_apply` or `after_fetch` fails, a warning is printed but processing continues.

#### Combining fragment and target actions

When both fragment and target actions are defined, they execute in this order:

1. Fragment's `before_*` action
2. For each target:
    - Target's `before_*` action
    - File copy operation
    - Target's `after_*` action
3. Fragment's `after_*` action

Example with both fragment and target actions:

```toml
[my_app]
targets = [
    { src = "~/.config/my_app", actions = { after_apply = "my_app --reload-config" } },
    { src = "~/.local/share/my_app/data" },
]

[my_app.actions]
before_apply = "my_app --stop"
after_apply = "my_app --start"
```

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

### Apply configuration

Copy files from the repository to your system:

```bash
# Apply all fragments
nastrajacz --apply

# Apply specific fragments
nastrajacz --apply --select nvim,git
```

### List fragments

Display all fragments defined in the configuration:

```bash
nastrajacz --list
```

### Command reference

| Command                | Description                                      |
| ---------------------- | ------------------------------------------------ |
| `--fetch`              | Fetch configuration from system to repository.   |
| `--apply`              | Apply configuration from repository to system.   |
| `--list`               | List all available fragments.                    |
| `--select <fragments>` | Comma-separated list of fragments to operate on. |
| `--help`               | Show help message.                               |

## Directory structure

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

## Example workflow

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
