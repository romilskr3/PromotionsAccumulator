from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from fetchers._shared.models import DUBLIN

REPO_ROOT = Path(__file__).resolve().parents[2]
LEAFLETS_ROOT = REPO_ROOT / "leaflets"
DEFAULT_MAX_AGE = timedelta(hours=24)


def week_dir(store: str, promo_from: date, promo_until: date) -> Path:
    name = f"{promo_from.isoformat()}_{promo_until.isoformat()}"
    path = LEAFLETS_ROOT / store.lower() / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def meta_path(week_path: Path) -> Path:
    return week_path / "meta.json"


def publication_path(week_path: Path) -> Path:
    return week_path / "publication.json"


def write_meta(
    week_path: Path,
    *,
    store: str,
    source_url: str,
    promo_from: date,
    promo_until: date,
    label: str = "",
    extra: dict[str, Any] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "store": store,
        "source_url": source_url,
        "promo_from": promo_from.isoformat(),
        "promo_until": promo_until.isoformat(),
        "label": label,
        "downloaded_at": datetime.now(DUBLIN).isoformat(),
    }
    if extra:
        payload.update(extra)
    meta_path(week_path).write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )


def read_meta(week_path: Path) -> dict[str, Any]:
    return json.loads(meta_path(week_path).read_text(encoding="utf-8"))


def write_publication(week_path: Path, data: Any) -> None:
    publication_path(week_path).write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def read_publication(week_path: Path) -> Any:
    return json.loads(publication_path(week_path).read_text(encoding="utf-8"))


def is_stale(week_path: Path, max_age: timedelta = DEFAULT_MAX_AGE) -> bool:
    meta = meta_path(week_path)
    if not meta.exists():
        return True
    if not publication_path(week_path).exists():
        return True
    try:
        data = read_meta(week_path)
        downloaded_at = datetime.fromisoformat(data["downloaded_at"])
        if downloaded_at.tzinfo is None:
            downloaded_at = downloaded_at.replace(tzinfo=DUBLIN)
        age = datetime.now(DUBLIN) - downloaded_at.astimezone(DUBLIN)
        return age > max_age
    except (KeyError, ValueError, json.JSONDecodeError):
        return True


def dublin_today() -> date:
    return datetime.now(DUBLIN).date()


def week_promo_dates(week_path: Path) -> tuple[date, date] | None:
    try:
        meta = read_meta(week_path)
        return (
            date.fromisoformat(meta["promo_from"]),
            date.fromisoformat(meta["promo_until"]),
        )
    except (KeyError, ValueError, json.JSONDecodeError, FileNotFoundError):
        return None


def best_cached_week_dir(store: str, *, today: date | None = None) -> Path | None:
    """Prefer a cached week that is still valid today; else the latest promo_until."""
    today = today or dublin_today()
    dirs = list_week_dirs(store)
    if not dirs:
        return None

    active: list[tuple[date, date, Path]] = []
    dated: list[tuple[date, date, Path]] = []
    for path in dirs:
        bounds = week_promo_dates(path)
        if not bounds or not (path / "leaflet.pdf").exists():
            continue
        promo_from, promo_until = bounds
        dated.append((promo_until, promo_from, path))
        if promo_from <= today <= promo_until:
            active.append((promo_until, promo_from, path))

    if active:
        return max(active)[2]
    if dated:
        return max(dated)[2]
    return dirs[-1]


def list_week_dirs(store: str) -> list[Path]:
    store_path = LEAFLETS_ROOT / store.lower()
    if not store_path.exists():
        return []
    dirs = []
    for path in sorted(store_path.iterdir()):
        if not path.is_dir():
            continue
        if path.name == "super-savers":
            continue
        if (
            publication_path(path).exists()
            or meta_path(path).exists()
            or (path / "fresh-4.json").exists()
        ):
            dirs.append(path)
    return dirs
