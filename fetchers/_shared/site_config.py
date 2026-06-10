from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from fetchers._shared.frequent_buy import DEFAULT_FAVOURITE_KEYWORDS, FREQUENT_BUY_KEYWORDS
_DEFAULT_OWNER = "romilskr3"
_DEFAULT_REPO = "PromotionsAccumulator"


def github_repo() -> tuple[str, str]:
    try:
        url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            text=True,
            stderr=subprocess.DEVNULL,
            cwd=Path(__file__).resolve().parents[2],
        ).strip()
        match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$", url)
        if match:
            return match.group("owner"), match.group("repo")
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return _DEFAULT_OWNER, _DEFAULT_REPO


def site_config_dict() -> dict[str, Any]:
    owner, repo = github_repo()
    slug = f"{owner}/{repo}"
    return {
        "owner": owner,
        "repo": repo,
        "slug": slug,
        "workflowUrl": (
            f"https://github.com/{owner}/{repo}/actions/workflows/"
            "refresh-promotions.yml"
        ),
        "workflowFile": "refresh-promotions.yml",
        "frequentBuyKeywords": list(FREQUENT_BUY_KEYWORDS),
        "favouriteKeywords": {
            category: list(keywords)
            for category, keywords in DEFAULT_FAVOURITE_KEYWORDS.items()
        },
    }


def write_site_config(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    cfg = site_config_dict()

    existing_token = ""
    if path.is_file():
        try:
            existing_token = json.loads(path.read_text(encoding="utf-8")).get(
                "refreshDispatchToken", ""
            )
        except (json.JSONDecodeError, OSError):
            existing_token = ""

    token = os.environ.get("REFRESH_DISPATCH_TOKEN", "").strip() or str(
        existing_token or ""
    ).strip()
    if token:
        cfg["refreshDispatchToken"] = token

    path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    return path
