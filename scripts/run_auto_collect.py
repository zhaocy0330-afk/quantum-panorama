from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from quantum_panorama.collectors.pipeline import collect_sources
from quantum_panorama.collectors.source_registry import DEFAULT_RESEARCH_SOURCES
from quantum_panorama.storage import database as db


def main() -> None:
    db.init_db()
    if db.get_data_sources().empty:
        db.add_default_sources(DEFAULT_RESEARCH_SOURCES)
    sources = db.get_data_sources(enabled_only=True)
    if sources.empty:
        print("No enabled data sources. Nothing to collect.")
        return
    result = collect_sources([], limit=3, timeout=5)
    print(f"Auto collect finished. found={result['total_found']} saved={result['total_saved']}")
    if result["errors"]:
        print("Errors:")
        for error in result["errors"]:
            print(f"- {error}")


if __name__ == "__main__":
    main()
