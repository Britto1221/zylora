from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path("apps/api").resolve()))

from app.db.base import Base
from app.db.seed import seed_development
from app.db.session import SessionLocal, engine


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_development(db)
    print("Development data is ready.")


if __name__ == "__main__":
    main()
