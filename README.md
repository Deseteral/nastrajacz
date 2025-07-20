# Nastrajacz

Simple configuration manager. Can be used to manage anything from dotfiles to server configuration.

It operates on fragments - configuration groups (that could correspond to programs for example).
Each fragment can have more then one file/directory that is going to process - targets.

Fragments and their targets are defined in `fragments.toml` file in the root of the repository where files are versioned.
Example:

```toml
[nvim]
targets = [
    { src = "~/.config/nvim", dir = "config" },
]
```

For more real-life example check out my [dotfiles](https://github.com/Deseteral/dotfiles).

For program documentation run:

```bash
nastrajacz --help
```

## 📜 License

This project is licensed under the [MIT license](LICENSE).
