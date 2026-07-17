#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from uuid import NAMESPACE_DNS, UUID, uuid5

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from app.db.session import SessionLocal  # noqa: E402
from app.modules.exports.service import build_client_export  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export one Zylora client's static standalone site package."
    )
    parser.add_argument("--client_id", required=True, help="Tenant UUID")
    parser.add_argument(
        "--output_dir",
        default=str(ROOT / "exports"),
        help="Directory where the zip should be written",
    )
    args = parser.parse_args()

    try:
        tenant_id = UUID(args.client_id)
    except ValueError as exc:
        raise SystemExit("--client_id must be a valid tenant UUID") from exc

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    system_actor = uuid5(NAMESPACE_DNS, "zylora-export-cli")

    with SessionLocal() as db:
        try:
            final_zip = build_client_export(
                db,
                tenant_id=tenant_id,
                actor_user_id=system_actor,
                output_dir=output_dir,
            )
            db.commit()
        except Exception:
            db.rollback()
            raise

    print(final_zip)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
