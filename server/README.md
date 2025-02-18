# Cat API Server

## Install Poetry

It is recommended to use Python virtual environment, so you don't pollute your system Python environment.

```bash
# Install dependencies
poetry install
```

```bash
# Activate Python Virtual Environment for Mac/Linux
eval "$(poetry env activate)"

# Activate Python Virtual Environment for Windows
.venv\Scripts\Activate.ps1
```

## Set up environment variables

```bash
# Create .env file (by copying from .env.example)
cp .env.example .env
```

## Style Enforcement

```bash
black . # Check Python code style
isort . # Sort Python imports
```

## Quick Start

To spin up the server, run the following command at the `server` directory:

```bash
poetry run uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8080 --env-file .env
```

## Debugging notes

### Configure VSCode Python Interpreter to use Poetry's virtual environment

1. Close VSCode so that it is able to detect the newly created virtual environment. A lot of times, this alone is enough to fix the issue.
2. In the command palette, type `Python: Select Interpreter`
3. Type `poetry` in the search box
4. The first option should be what you want to use

### Library is installed in virtual environment, recognised by VSCode but not by the server

1. It is because uvicorn is not installed in this virtual environment and you are running uvicorn from another virtual environment in another project.
2. Make sure to install the necessary libraries so that the python executable runs from the correct project `poetry add uvicorn python-dotenv`
