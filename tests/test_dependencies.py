import functools
import itertools
import pathlib
import shutil
import typing

import pytest
from packaging.requirements import Requirement

from fromager import context, dependencies

_fromager_root = pathlib.Path(__file__).parent.parent


@pytest.mark.parametrize(
    "build_system,expected_results",
    [
        # Empty
        ({}, dependencies._DEFAULT_BACKEND),
        # Only specify requirements (pyarrow)
        (
            {"requires": ["a-dep"]},
            {
                "build-backend": "setuptools.build_meta:__legacy__",
                "backend-path": None,
                "requires": ["a-dep"],
            },
        ),
        # Specify everything
        (
            {
                "build-backend": "setuptools.build_meta:__legacy__",
                "backend-path": None,
                "requires": ["a-dep"],
            },
            {
                "build-backend": "setuptools.build_meta:__legacy__",
                "backend-path": None,
                "requires": ["a-dep"],
            },
        ),
    ],
)
def test_get_build_backend(
    build_system: dict[str, list[str]] | dict[str, str | list[str] | None],
    expected_results: dict[str, typing.Any] | dict[str, str | list[str] | None],
):
    pyproject_toml = {"build-system": build_system}
    actual = dependencies.get_build_backend(pyproject_toml)
    assert expected_results == actual


def _clean_build_artifacts(f):
    @functools.wraps(f)
    def _with_cleanup(*args, **kwds):
        try:
            f(*args, **kwds)
        finally:
            for d in itertools.chain(
                _fromager_root.glob("fromager-*.dist-info"),
                _fromager_root.glob("fromager.egg-info"),
            ):
                shutil.rmtree(d)


@_clean_build_artifacts
def test_get_build_system_dependencies(tmp_context: context.WorkContext):
    results = dependencies.get_build_system_dependencies(
        tmp_context,
        Requirement("fromager"),
        _fromager_root,
    )
    names = set(r.name for r in results)
    assert names == set(["setuptools", "setuptools_scm"])


@_clean_build_artifacts
def test_get_build_backend_dependencies(tmp_context: context.WorkContext):
    results = dependencies.get_build_backend_dependencies(
        tmp_context,
        Requirement("fromager"),
        _fromager_root,
    )
    names = set(r.name for r in results)
    assert names == set()


@_clean_build_artifacts
def test_get_build_sdist_dependencies(tmp_context: context.WorkContext):
    results = dependencies.get_build_sdist_dependencies(
        tmp_context,
        Requirement("fromager"),
        _fromager_root,
    )
    names = set(r.name for r in results)
    assert names == set()


@_clean_build_artifacts
def test_get_install_dependencies(tmp_context: context.WorkContext):
    pyproject_contents = dependencies.get_pyproject_contents(_fromager_root)
    expected = set(
        Requirement(d) for d in pyproject_contents["project"]["dependencies"]
    )
    actual = dependencies.get_install_dependencies(
        tmp_context,
        Requirement("fromager"),
        _fromager_root,
    )
    assert actual == expected
