"""Run the full Andes→Drye example pipeline."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
STEPS = [
  "01_build_and_calibrate.py",
  "02_analyze_in_domain_a.py",
  "03_analyze_out_domain_b.py",
  "04_compare_and_document.py",
]


def main() -> int:
  for step in STEPS:
    path = SCRIPTS / step
    print(f"\n=== {step} ===")
    proc = subprocess.run([sys.executable, str(path)], check=False)
    if proc.returncode != 0:
      print(f"FAILED {step} with exit {proc.returncode}", file=sys.stderr)
      return proc.returncode
  print("\nAll example steps completed.")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
