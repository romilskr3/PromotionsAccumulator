from __future__ import annotations

import os
from pathlib import Path

from fetchers._shared.leaflet_cache import LEAFLETS_ROOT


class TescoSessionError(RuntimeError):
    """Tesco Fresh 4 requires a valid saved Playwright browser session."""


def storage_state_path() -> Path:
    env_path = os.environ.get("TESCO_STORAGE_STATE")
    if env_path:
        return Path(env_path)
    return LEAFLETS_ROOT / "tesco" / "storage-state.json"


def has_storage_state() -> bool:
    return storage_state_path().is_file()
