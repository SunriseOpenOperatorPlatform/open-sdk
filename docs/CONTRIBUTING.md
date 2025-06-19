# Contributing to OpenSDK

Thank you for considering contributing to OpenSDK! This guide outlines how to contribute code, report issues, and ensure consistency across submissions.

---

## Getting Started

To contribute:

1. Fork the repository and create a feature branch from `main`.
2. Develop your changes in the appropriate adapter directory:
   - `src/sunrise6g_opensdk/edgecloud/clients/`
   - `src/sunrise6g_opensdk/network/clients/`
   - `src/sunrise6g_opensdk/oran/clients/`
3. Follow the coding guidelines below.
4. Write or update unit tests for your changes.
5. Ensure all tests pass.
6. Set up and run `pre-commit` hooks before pushing changes.
7. Submit a pull request with a clear and concise description.

---

## Branch Naming Convention

Choose a branch name that reflects the adapter type and your feature:

- `feature/add-edgecloud-<platform>`
- `feature/add-network-<5gcore>`
- `feature/add-oran-<solution>`

Examples:
```bash
feature/add-edgecloud-i2edge
feature/add-network-open5gs
feature/add-oran-juniper
```

---

## Coding Guidelines

- Write meaningful commit messages.
- Keep pull requests focused and concise.
- Document public methods and classes using docstrings.

---

## Pre-commit Hook Setup

We use `pre-commit` to enforce formatting and static analysis. Apply these commands from the root of the repository:

### Initial Setup

```bash
pip3 install pre-commit
pre-commit install
```

### Optional (Run hooks manually or before commit)

```bash
pre-commit run --all-files
```

---

## Testing

Before submitting your contribution, ensure all unit tests pass.

See [TESTING.md](TESTING.md) for instructions.

---

## Reporting Issues

Please use the [Issue Tracker](https://github.com/SunriseOpenOperatorPlatform/sunrise6g-opensdk/issues) for bug reports or feature requests.

When reporting a bug, include:

- A clear description of the problem
- Steps to reproduce it
- Relevant logs or error messages (if any)

---

## Code of Conduct

We are committed to maintaining a welcoming and respectful environment for all contributors.

---

Thank you for helping improve OpenSDK!
