import subprocess
import sys


def main():
    commands = [
        [
            "poetry",
            "run",
            "autoflake",
            "--remove-all-unused-imports",
            "--in-place",
            "--recursive",
            "--exclude=__init__.py",
            "--ignore-pass-after-docstring",
            ".",
        ],
        ["poetry", "run", "black", "."],
        ["poetry", "run", "isort", "."],
    ]

    for command in commands:
        result = subprocess.run(command)
        if result.returncode != 0:
            print(f"Command failed: {' '.join(command)}", file=sys.stderr)
            sys.exit(result.returncode)


if __name__ == "__main__":
    main()
