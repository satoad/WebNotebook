#!/usr/bin/env python3
"""Default: create doc"""
import os


DOIT_CONFIG = {'default_tasks': ['html']}


def task_test():
    """Запускает тестирование модуля"""
    return {
        "actions": ["python3 -m unittest -v test.py"],
        "file_dep": ["test.py"],
    }


def task_html():
    """Создаёт документацию"""
    return {
        'actions': ['sphinx-build -M html doc/source doc/build'],
    }


def task_whl():
    """Создаёт колесо"""
    return {
        "actions": ["python3 -m build -w"],
        "file_dep": ['pyproject.toml'],
        "targets": ['dist/*.whl'],
    }


def task_babel():
    """Создаёт переводы"""
    return {
        "actions": ["pybabel compile -D webnotebook -d webnotebook/po -l ru"],
    }
