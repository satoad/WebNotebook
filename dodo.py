import os

def task_test_client():
    return {
        "actions": ["python3 -m unittest -v test.py"],
        "file_dep": ["test.py"],
    }


def task_html():
    return {
        'actions': ['sphinx-build -M html doc/source doc/build'],
    }


def task_whl():
    return {
        "actions": ["python3 -m build --wheel"],
        "file_dep": ['pyproject.toml'],
        "targets": ['dist/*.whl'],
    }


def task_babel():
    return {
        "actions": ["pybabel compile -D webnotebook -d po -l ru"],
    }

