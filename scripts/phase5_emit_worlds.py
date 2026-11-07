#!/usr/bin/env python3
"""Emit Phase 5 MVP multi-world family report (no holdout fitting)."""

from __future__ import annotations

import json
from pathlib import Path

from medicare_synth.calibration import load_default_corpus
from medicare_synth.evaluation import (
  assert_hard_gates_documented,
  load_evaluation_freeze,
)
from medicare_synth.worlds import emit_world_family, family_summary

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "phase5"


def main() -> None:
  corpus, path = load_default_corpus()
  freeze = load_evaluation_freeze(corpus=corpus)
  assert_hard_gates_documented(freeze)
  family = emit_world_family(
    corpus=corpus,
    corpus_path=path,
    freeze=freeze,
    n_beneficiaries=6000,
    seed=42,
  )
  OUT_DIR.mkdir(parents=True, exist_ok=True)
  summary = family_summary(family)
  summary["evaluation_freeze"] = freeze.model_dump(mode="json")
  summary["non_claims"] = [
    "Synthetic agreement is not a Medicare finding.",
    "Holdout was evaluate-only; not used for fitting or selection.",
  ]
  (OUT_DIR / "world_family_summary.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
  )
  freeze_path = OUT_DIR / "evaluation_freeze.json"
  freeze_path.write_text(
    freeze.model_dump_json(indent=2) + "\n",
    encoding="utf-8",
  )
  for w in family.worlds:
    manifest_path = OUT_DIR / f"manifest_{w.world_id}.json"
    manifest_path.write_text(w.run_manifest.to_json() + "\n", encoding="utf-8")
  print(f"wrote {OUT_DIR / 'world_family_summary.json'}")
  print(f"family_sha256={family.sha256()}")
  for w in family.worlds:
    print(
      f"{w.world_id}: cal_mae "
      f"{w.calibration_baseline.mean_absolute_error} -> "
      f"{w.calibration_fitted.mean_absolute_error}; "
      f"structural={w.structural_valid}; improved={w.improved_calibration}"
    )


if __name__ == "__main__":
  main()
