from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

REFRESH_ISSUE_TITLE = "[refresh-promotions]"
REFRESH_ISSUE_BODY = "Refresh requested from the promotions site."

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


def site_config_dict() -> dict[str, str]:
    owner, repo = github_repo()
    slug = f"{owner}/{repo}"
    issue_title = quote(REFRESH_ISSUE_TITLE)
    issue_body = quote(REFRESH_ISSUE_BODY)
    return {
        "owner": owner,
        "repo": repo,
        "slug": slug,
        "refreshIssueTitle": REFRESH_ISSUE_TITLE,
        "issueRefreshUrl": (
            f"https://github.com/{owner}/{repo}/issues/new"
            f"?title={issue_title}&body={issue_body}"
        ),
        "workflowUrl": (
            f"https://github.com/{owner}/{repo}/actions/workflows/"
            "refresh-promotions.yml"
        ),
    }


def write_site_config(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(site_config_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    return path
