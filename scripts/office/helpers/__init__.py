"""Shared helpers for the office toolchain.

`OOXML_FAMILY`, `safe_extract` and `rezip` are taken from the official Anthropic pptx
skill (snapshot in `vendor/pptx-official-2026-07-29/`). They are vendored rather than
rewritten because they solve three things we need and got wrong or lacked:

* `OOXML_FAMILY` maps the TEMPLATE extensions too, so `--original sfnl-sjabloon.potx`
  works. Our template is a .potx, and baselining a build against it is the whole point
  of `--original`; the old suffix check rejected it outright.
* `safe_extract` refuses symlink entries and paths that escape the destination, unlike
  `zf.extractall`, which will happily write outside the target directory.
* `rezip` writes to a temp file and `os.replace`s it into place, so an interrupted write
  cannot leave a half-written deck, and it stores `[Content_Types].xml` first and
  uncompressed, which is what OPC readers expect.
"""

import os
import posixpath
import re
import stat
import tempfile
import urllib.parse
import zipfile
from pathlib import Path

OOXML_FAMILY = {
    ".docx": "docx",
    ".dotx": "docx",
    ".pptx": "pptx",
    ".potx": "pptx",
    ".xlsx": "xlsx",
    ".xltx": "xlsx",
}

SLIDE_REL_TYPE = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
)

_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*:")


def opc_target(target: str, source_part: str, target_mode: str = "") -> str | None:
    """Resolve a relationship Target to a package part name, or None if it is external.

    OPC part names are POSIX and may be relative to the source part's directory, so
    joining them by hand with os.path gets it wrong on Windows and misses the
    `..`-escape and absolute-target cases entirely.
    """
    if not target:
        return None
    if target_mode.lower() == "external":
        return None
    target = urllib.parse.unquote(target)

    if _SCHEME_RE.match(target):
        return None

    if "\\" in target:
        raise ValueError(f"relationship target is not a POSIX part name: {target!r}")

    if target.startswith("/"):
        joined = target.lstrip("/")
    else:
        joined = posixpath.join(posixpath.dirname(source_part), target)

    parts: list[str] = []
    for segment in posixpath.normpath(joined).split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            if not parts:
                raise ValueError(f"relationship target escapes the package: {target!r}")
            parts.pop()
        else:
            parts.append(segment)

    if not parts:
        raise ValueError(f"relationship target resolves to nothing: {target!r}")
    return "/".join(parts)


def safe_extract(zf: zipfile.ZipFile, dest: Path) -> None:
    """Extract every entry, refusing symlinks and paths that escape `dest`."""
    dest = dest.resolve()
    for member in zf.infolist():
        if stat.S_ISLNK(member.external_attr >> 16):
            raise ValueError(f"symlink archive entry not allowed: {member.filename!r}")
        target = (dest / member.filename).resolve()
        if not target.is_relative_to(dest):
            raise ValueError(f"unsafe archive entry: {member.filename!r}")
        zf.extract(member, dest)


def rezip(src_dir: Path, out_path: Path) -> None:
    """Zip `src_dir` into `out_path` atomically, content types first and stored."""
    files = sorted(p for p in src_dir.rglob("*") if p.is_file())
    content_types = src_dir / "[Content_Types].xml"
    fd, tmp_name = tempfile.mkstemp(
        prefix=out_path.name + ".", suffix=".tmp", dir=out_path.parent
    )
    tmp_out = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            with zipfile.ZipFile(handle, "w", zipfile.ZIP_DEFLATED) as zf:
                if content_types.exists():
                    zf.write(
                        content_types,
                        content_types.relative_to(src_dir),
                        compress_type=zipfile.ZIP_STORED,
                    )
                for f in files:
                    if f == content_types:
                        continue
                    zf.write(f, f.relative_to(src_dir))
        if out_path.exists():
            mode = out_path.stat().st_mode & 0o777
        else:
            umask = os.umask(0)
            os.umask(umask)
            mode = 0o666 & ~umask
        os.chmod(tmp_out, mode)
        os.replace(tmp_out, out_path)
    finally:
        if tmp_out.exists():
            tmp_out.unlink()
