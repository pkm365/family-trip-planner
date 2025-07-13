"""Cleanup script for activity_recommendations table.

Removes recommendations that lack both description and primary_image_url
(i.e., low-quality placeholder results).

Usage:
    python scripts/cleanup_old_recommendations.py
"""

import sys
from pathlib import Path

# Ensure project root on PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database import SessionLocal
from backend.models import ActivityRecommendation


def cleanup() -> None:
    db = SessionLocal()
    try:
        query = db.query(ActivityRecommendation).filter(
            ActivityRecommendation.primary_image_url.is_(None),
            ActivityRecommendation.description.is_(None)
        )
        count = query.count()
        if count == 0:
            print("No low-quality recommendations found. Nothing to delete.")
            return

        print(f"Found {count} low-quality recommendations. Deleting…")
        deleted = 0
        for rec in query.all():
            print(f"  - {rec.id}: {rec.name}")
            db.delete(rec)
            deleted += 1
        db.commit()
        print(f"Cleanup complete. {deleted} records deleted.")
    except Exception as exc:
        db.rollback()
        print(f"Error during cleanup: {exc}")
    finally:
        db.close()


if __name__ == "__main__":
    cleanup() 