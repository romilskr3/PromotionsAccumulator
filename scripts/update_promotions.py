#!/usr/bin/env python3
"""Master script: run store fetchers and update output/promotions.md."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fetchers._shared.publish import write_all_outputs
from fetchers.registry import STORES, fetch_all


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch supermarket fruit/veg promotions and update output files."
    )
    parser.add_argument(
        "--store",
        action="append",
        dest="stores",
        choices=list(STORES.keys()),
        help="Fetch only these stores (can repeat). Default: all.",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip leaflet downloads; parse cached leaflets only.",
    )
    parser.add_argument(
        "--refresh-leaflets",
        action="store_true",
        help="Force re-download of leaflet data even if cache is fresh.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    try:
        promotions = fetch_all(
            stores=args.stores,
            skip_download=args.skip_download,
            refresh_leaflets=args.refresh_leaflets,
        )
    except RuntimeError as exc:
        logging.error("%s", exc)
        return 1

    outputs = write_all_outputs(promotions)
    print(f"Wrote {len(promotions)} promotion(s):")
    print(f"  Markdown: {outputs['markdown']}")
    print(f"  HTML:     {outputs['html']}")
    print(f"  Pages:    {outputs['pages']}  (commit docs/ and push for GitHub Pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
