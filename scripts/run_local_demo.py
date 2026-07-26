#!/usr/bin/env python3
"""Launch the SiliconPulse no-Docker local demo.

Usage:
  python scripts/run_local_demo.py
  python scripts/run_local_demo.py --port 8787
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLATFORM = ROOT / "apps" / "local_platform"
sys.path.insert(0, str(PLATFORM))

from server import main  # noqa: E402


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SiliconPulse AI local demo (stdlib only)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    main(host=args.host, port=args.port)
