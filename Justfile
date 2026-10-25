venv := env_var('HOME') / ".venvs/ovos-gui1"

test:
    {{venv}}/bin/python -m pytest -q

lint:
    ruff check --line-length 130 .
    ruff format --check --line-length 130 .

install:
    uv pip install --python {{venv}}/bin/python --no-deps -e .
