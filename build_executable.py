"""Utility helpers to build the Bibliostratus Windows executable with PyInstaller.

The historical build process was a thin wrapper around ``pyinstaller main.py``.
When Bibliostratus started targeting Python 3.10 the generated archive missed the
``_tkinter`` extension and the associated Tcl/Tk runtime.  The resulting
``main.exe`` therefore crashed as soon as ``import tkinter`` was executed with::

    ImportError: DLL load failed while importing _tkinter

PyInstaller normally bundles these libraries automatically, but only when the
current interpreter exposes them.  Some environments were created from Python
installations that lacked the Tk bindings, which meant PyInstaller silently
skipped the files.  ``build_executable.py`` makes the failure explicit and adds
``--add-data`` directives so that the Tcl/Tk runtime is always copied next to
``main.exe``.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import PyInstaller.__main__


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = PROJECT_ROOT / "bibliostratus"


PathLikePair = Tuple[Path, Path]


def _check_module_available(module_name: str) -> None:
    """Abort the build with a readable error message when *module_name* is missing."""

    spec = importlib.util.find_spec(module_name)
    if spec is None:
        raise SystemExit(
            f"The Python interpreter located at {Path(sys.executable)} does not "
            f"provide the '{module_name}' module. Please install a Python "
            "distribution that ships with Tk support (for example the official "
            "python.org installer) before trying to compile Bibliostratus."
        )


def _candidate_tcl_roots(tkinter_module: importlib.machinery.ModuleSpec) -> Iterable[Path]:
    """Yield directories that may contain Tcl/Tk data files."""

    module_path = Path(tkinter_module.origin).resolve()
    # ``tkinter`` lives in ``Lib/tkinter/__init__.py`` on Windows.
    # Depending on how Python was installed, the Tcl data can be stored in
    # ``<prefix>/tcl`` or ``<prefix>/Lib/tcl``.  The ``DLLs`` directory sits next
    # to ``python.exe``.
    prefix = module_path.parents[2]
    yield prefix
    yield prefix / "tcl"
    yield prefix / "Lib" / "tcl"
    yield module_path.parent / "tcl"


def _discover_tk_data() -> List[PathLikePair]:
    """Locate Tcl/Tk resource directories and runtime DLLs.

    The returned list contains ``(source, destination)`` pairs that can be
    transformed into ``PyInstaller --add-data`` arguments.
    """

    tkinter_spec = importlib.util.find_spec("tkinter")
    if tkinter_spec is None or tkinter_spec.origin is None:
        raise SystemExit(
            "tkinter could not be imported. PyInstaller cannot create a GUI "
            "binary without it."
        )

    _check_module_available("_tkinter")

    module_path = Path(tkinter_spec.origin).resolve()
    dll_candidates = [module_path.parents[2] / "DLLs", module_path.parent]

    tcl_root = next((candidate for candidate in _candidate_tcl_roots(tkinter_spec) if candidate.exists()), None)
    if tcl_root is None:
        raise SystemExit(
            "Unable to locate the Tcl/Tk resource directory. Set the TK/TCL "
            "related environment variables or install the optional Tk component "
            "for your Python interpreter."
        )

    data_pairs: List[PathLikePair] = []

    for entry in sorted(tcl_root.iterdir()):
        if entry.is_dir():
            name = entry.name.lower()
            if name.startswith("tk"):
                data_pairs.append((entry, Path("tk") / entry.name))
            elif name.startswith("tcl"):
                data_pairs.append((entry, Path("tcl") / entry.name))
        elif entry.suffix.lower() == ".dll":
            lower_name = entry.name.lower()
            if lower_name.startswith("tcl") or lower_name.startswith("tk"):
                data_pairs.append((entry, Path(".")))

    for dll_dir in dll_candidates:
        if not dll_dir.exists():
            continue
        for pattern in ("tcl*.dll", "tk*.dll"):
            for dll in dll_dir.glob(pattern):
                pair = (dll, Path("."))
                if pair not in data_pairs:
                    data_pairs.append(pair)

    if not data_pairs:
        raise SystemExit(
            "Tcl/Tk libraries were not found. Reinstall Python with Tk support "
            "and retry."
        )

    return data_pairs


def _to_add_data_arguments(pairs: Sequence[PathLikePair]) -> Iterable[str]:
    """Convert ``(source, destination)`` pairs into PyInstaller ``--add-data`` arguments."""

    for src, dst in pairs:
        yield f"{src}{os.pathsep}{dst.as_posix()}"


def build_executable(extra_args: Sequence[str] | None = None) -> None:
    """Run PyInstaller with Bibliostratus specific defaults."""

    if not SOURCE_DIR.exists():
        raise SystemExit(f"The Bibliostratus sources were not found at {SOURCE_DIR}.")

    args: List[str] = [
        str(SOURCE_DIR / "main.py"),
        "--name",
        "main",
        "--clean",
        "--noconfirm",
        "--exclude-module",
        "numpy",
        "--exclude-module",
        "pandas",
        "--exclude-module",
        "scipy",
        "--exclude-module",
        "notebook",
        "--exclude-module",
        "matplotlib",
    ]

    for add_data in _to_add_data_arguments(_discover_tk_data()):
        args.extend(["--add-data", add_data])

    if extra_args:
        args.extend(extra_args)

    previous_cwd = Path.cwd()
    os.chdir(SOURCE_DIR)
    try:
        PyInstaller.__main__.run(args)
    finally:
        os.chdir(previous_cwd)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build the Bibliostratus executable with PyInstaller")
    parser.add_argument(
        "pyinstaller_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments forwarded to PyInstaller",
    )
    parsed = parser.parse_args(argv)
    build_executable(parsed.pyinstaller_args)


if __name__ == "__main__":
    main()
