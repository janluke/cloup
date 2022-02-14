import pathlib

import click

import cloup


def test_path():
    p = cloup.path()
    assert isinstance(p, click.Path)
    assert p.type == pathlib.Path


def test_dir_path():
    p = cloup.dir_path()
    assert isinstance(p, click.Path)
    assert p.type == pathlib.Path
    assert not p.file_okay
    assert p.dir_okay


def test_file_path():
    p = cloup.file_path()
    assert isinstance(p, click.Path)
    assert p.type == pathlib.Path
    assert not p.dir_okay
    assert p.file_okay
