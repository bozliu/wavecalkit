"""Source-checkout shim for `python -m wavecal.cli`.

The installable package lives under `src/wavecal`. This small namespace shim
keeps local examples runnable before an editable install.
"""

from pathlib import Path

_src_package = Path(__file__).resolve().parent.parent / "src" / "wavecal"
if _src_package.exists():
    __path__.append(str(_src_package))
