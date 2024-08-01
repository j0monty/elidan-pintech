# Elidan PinTech

blah blah blah...

## Structure

```
├── BUILD
├── LICENSE
├── README.md
├── pants.toml
├── scripts/
├── src
│   ├── docker
│   │   ├── mongo/                - mongo container
│   │   └── pintech_api-server/   - pintech api container
│   ├── python
│   │   ├── common/               - where common shared libs go
│   │   ├── services/             - 1 service per folder
│   │   │   └── pintech_api/      - pintech_api fastapi service
│   │   └── tests                 - unit tests
└── start-pintech.sh              - script to start services
```

## Commands

To run linters / mypy, formatting, etc. install pre-commit hooks

```bash
$ pre-commit install
```

To run the PinTech API:

```bash
$ ./start-pintech.sh
```

To build packages, containers, etc (WIP)

```bash
$ pants package ::
```

# Setting up Dev env

1. Install `pants`
2. Setup virtual env (pyenv, etc) for python 3.12.x
3. Install docker desktop
4. install dependencies using poetry install in src/python/services/pintech_api/

## Setting up IDE and using pants build

https://www.pantsbuild.org/

If you use a code-aware editor or IDE, such as PyCharm or VSCode, you may want to set it up to understand your code layout and dependencies. This will allow it to perform code navigation, auto-completion and other features that rely on code comprehension.

There are two scripts in `scripts/` folder that can help with this:

More info on this here: https://www.pantsbuild.org/2.18/docs/using-pants/setting-up-an-ide

pants goals:

```bash
$ pants help goals
```

chain commands:

```bash
$ pants lint test ::
13:16:15.49 [INFO] Reading /Users/m0nty/code/elidan/elidan-pintech/pintech/.python-version to determine desired version for [python-bootstrap].search_path.
13:16:15.76 [INFO] Completed: Lint with `ruff check` - ruff check succeeded.
13:16:15.86 [INFO] Completed: Format with `ruff format` - ruff format made no changes.

✓ ruff check succeeded.
✓ ruff format succeeded.
13:16:15.87 [INFO] Completed: Run Pytest - src/tests/common/test_utils.py:tests - succeeded.

✓ src/tests/common/test_utils.py:tests succeeded in 0.42s (memoized).
```

Count lines of code:

```bash
$ pants count-loc ::                                                                                                                                                            { [ 1:12:19 ]
───────────────────────────────────────────────────────────────────────────────
Language                 Files     Lines   Blanks  Comments     Code Complexity
───────────────────────────────────────────────────────────────────────────────
Python                       8       145       28         5      112          8
TOML                         4       138       22        21       95          0
Markdown                     2        66       20         0       46          0
Shell                        2        37        5         8       24          0
gitignore                    1       318       66       109      143          0
───────────────────────────────────────────────────────────────────────────────
Total                       17       704      141       143      420          8
───────────────────────────────────────────────────────────────────────────────
Estimated Cost to Develop (organic) $10,864
Estimated Schedule Effort (organic) 2.466589 months
Estimated People Required (organic) 0.391315
───────────────────────────────────────────────────────────────────────────────
Processed 15289 bytes, 0.015 megabytes (SI)
───────────────────────────────────────────────────────────────────────────────
```
