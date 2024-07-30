# Elidan PinTech

blah blah blah...

## Structure

```
- scripts/
- src/
  - common/ (library shared by many services)
  - services/
    - pintech_api (main API service)
  - tests/
```

## Commands

To run linters / mypy, formatting, etc.

```bash
$ pants check ::    # runs mypy on all files
$ pants fmt ::      # ruff format on all files
$ pants lint ::     # runs ruff check & ruff format on all files
```

To run the PinTech API:

```bash
$ pants run src/services/pintech_api/main.py
```

To build services for running in a container, etc.

```bash
$ pants package ::
```

# Setting up Dev env

1. Install `pants`
2. Setup virtual env (pyenv, etc) for python 3.12.x

## Setting up IDE

If you use a code-aware editor or IDE, such as PyCharm or VSCode, you may want to set it up to understand your code layout and dependencies. This will allow it to perform code navigation, auto-completion and other features that rely on code comprehension.

There are two scripts in `scripts/` folder that can help with this:

More info on this here: https://www.pantsbuild.org/2.18/docs/using-pants/setting-up-an-ide

```bash
$ ./scripts/expose_library_roots_to_ide.sh
# essentially
$ ./pants export ::
```
