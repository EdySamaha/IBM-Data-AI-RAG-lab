#!/usr/bin/env python3
"""
Preflight check — run this once your environments exist and your .env is filled
in, to confirm everything is reachable BEFORE the lab starts.

It checks, in order and independently (one failure doesn't stop the rest):
  1. config/lab_config.yaml loads
  2. credentials are present (.env)
  3. watsonx.ai authentication works
  4. the Presto engine answers a COUNT on the catalogued table
  5. the Milvus engine accepts a connection

Nothing here mutates data. Missing credentials produce a friendly "not set"
line, not a crash — so it's safe to run even before you've filled in .env.

Usage:
    python scripts/verify_setup.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lab_helpers as lh  # noqa: E402

OK, BAD, SKIP = "[ OK ]", "[FAIL]", "[SKIP]"


def _print(status: str, msg: str) -> None:
    print(f"{status} {msg}")


def check_config() -> dict | None:
    try:
        cfg = lh.load_config()
        _print(OK, f"Config loaded — catalog={cfg['catalog']} schema={cfg['schema']} "
                   f"table={cfg['table']}")
        return cfg
    except Exception as e:  # noqa: BLE001
        _print(BAD, f"Could not load config/lab_config.yaml: {e}")
        return None


def check_credentials() -> bool:
    import os

    lh.load_env()
    required = ["IBM_CLOUD_API_KEY", "WATSONX_PROJECT_ID",
                "PRESTO_HOST", "PRESTO_USER", "PRESTO_PWD",
                "MILVUS_HOST", "MILVUS_PORT", "MILVUS_USER", "MILVUS_PWD"]
    missing = [k for k in required if not os.environ.get(k, "").strip()]
    if missing:
        _print(SKIP, "Credentials not set (fill in .env): " + ", ".join(missing))
        return False
    _print(OK, "All credentials present in the environment.")
    return True


def check_watsonx() -> bool:
    try:
        client = lh.get_client()
        _print(OK, f"watsonx.ai authenticated — SDK version {client.version}")
        return True
    except Exception as e:  # noqa: BLE001
        _print(BAD, f"watsonx.ai auth failed: {e}")
        return False


def check_presto(cfg: dict) -> bool:
    try:
        fq = f"{cfg['catalog']}.{cfg['schema']}.{cfg['table']}"
        df = lh.run_sql(f"SELECT count(*) AS n FROM {fq}")
        _print(OK, f"Presto reachable — {fq} has {df.iloc[0]['n']} rows.")
        return True
    except Exception as e:  # noqa: BLE001
        _print(BAD, f"Presto query failed (is the engine running? table ingested?): {e}")
        return False


def check_milvus() -> bool:
    try:
        import os
        from pymilvus import connections

        connections.connect(host=os.environ["MILVUS_HOST"],
                            port=os.environ["MILVUS_PORT"],
                            user=os.environ["MILVUS_USER"],
                            password=os.environ["MILVUS_PWD"], secure=True)
        _print(OK, "Milvus connection accepted.")
        connections.disconnect("default")
        return True
    except Exception as e:  # noqa: BLE001
        _print(BAD, f"Milvus connection failed (is the engine running?): {e}")
        return False


def main() -> int:
    print("=== watsonx lab preflight ===\n")
    cfg = check_config()
    have_creds = check_credentials()

    if not have_creds:
        print("\nFill in .env (copy from .env.template) and re-run to check "
              "connectivity. Config check above still tells you the names the "
              "lab expects.")
        return 0 if cfg else 1

    results = [check_watsonx()]
    if cfg:
        results.append(check_presto(cfg))
    results.append(check_milvus())

    print()
    if all(results) and cfg:
        print("All checks passed — you're ready for the lab.")
        return 0
    print("One or more checks failed — see the messages above.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
