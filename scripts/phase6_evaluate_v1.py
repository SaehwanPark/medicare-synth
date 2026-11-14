#!/usr/bin/env python3
"""Run the frozen Phase 6 protocol into a new, explicitly named output file."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

import polars as pl

from medicare_synth.calibration import load_default_corpus, structural_valid
from medicare_synth.evidence_corpus import PartitionName, sha256_file, verify_corpus_checksums
from medicare_synth.evaluation import load_evaluation_freeze
from medicare_synth.phase6 import WorkflowResult, analyze_workflow
from medicare_synth.synthesis import ConditionalWorldParams, generate_diabetes_ip_world
from medicare_synth.worlds import default_baseline_params, emit_world_family

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/phase6/protocol-v1.md"
SEEDS = (11, 42, 73)
N = 2000


def _git(*args: str) -> str:
  return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _hash(path: Path) -> str:
  return sha256_file(path)


def _duplicate_control(tables: dict[str, pl.DataFrame], result: WorkflowResult, weights: pl.DataFrame | None) -> bool:
  altered = dict(tables)
  altered["inpatient_claims"] = pl.concat([tables["inpatient_claims"]] * 2)
  return analyze_workflow(altered, weights=weights) == result


def _known_truth(seed: int) -> dict[str, Any]:
  params = ConditionalWorldParams(
    n_beneficiaries=N, seed=seed, diabetes_prevalence=0.30, hf_prevalence=0.20,
    p_ip_given_diabetes=0.20, p_ip_given_no_diabetes=0.04,
  )
  world = generate_diabetes_ip_world(params)
  observed = analyze_workflow(world.tables())
  specs = (
    ("diabetes_prevalence", 0.30, observed["n_eligible"]),
    ("hf_prevalence", 0.20, observed["n_eligible"]),
    ("ip_given_diabetes", 0.20, observed["n_diabetes"]),
    ("ip_given_no_diabetes", 0.04, observed["n_no_diabetes"]),
  )
  checks = {}
  for name, truth, count in specs:
    estimate = observed[name]  # type: ignore[literal-required]
    tolerance = max(0.03, 3.5 * math.sqrt(truth * (1 - truth) / count)) if count else None
    checks[name] = {
      "truth": truth, "estimate": estimate, "n": count, "tolerance": tolerance,
      "pass": estimate is not None and tolerance is not None and abs(float(estimate) - truth) <= tolerance,
    }
  return {"params": params.model_dump(mode="json"), "checks": checks, "structural_valid": structural_valid(world)}


def _run_seed(seed: int, corpus: Any, corpus_path: Path) -> dict[str, Any]:
  baseline = generate_diabetes_ip_world(default_baseline_params(n_beneficiaries=N, seed=seed))
  base_tables = baseline.tables()
  base = analyze_workflow(base_tables)
  family = emit_world_family(
    corpus=corpus, corpus_path=corpus_path, n_beneficiaries=N, seed=seed,
    diabetes_values=(0.18, 0.277, 0.32), hf_values=(0.04, 0.12),
    ip_diab_values=(0.05, 0.13),
  )
  worlds: dict[str, Any] = {}
  for w in family.worlds:
    tables = w.tables(raw=True) if w.weights is not None else w.tables()
    analysis = analyze_workflow(tables, weights=w.weights)
    worlds[w.world_id] = {
      "world_sha256": w.sha256(), "params": w.params.model_dump(mode="json"),
      "structural_valid": w.structural_valid,
      "calibration_targets": [r.model_dump(mode="json") for r in w.calibration_fitted.rows],
      "calibration_baseline_targets": [r.model_dump(mode="json") for r in w.calibration_baseline.rows],
      "calibration_baseline_mae": w.calibration_baseline.mean_absolute_error,
      "calibration_mae": w.calibration_fitted.mean_absolute_error,
      "calibration_n_missing": w.calibration_fitted.n_missing,
      "solver": dict(w.run_manifest.diagnostics),
      "holdout": w.holdout_report.model_dump(mode="json"),
      "holdout_exposure": "previously exposed diagnostic; not independent validation",
      "analyst": analysis,
      "raw_analyst": analyze_workflow(tables),
      "duplicate_claim_invariant": _duplicate_control(tables, analysis, w.weights),
      "weight_key": w.weight_key, "weight_method": w.weight_method,
      "weight_diagnostics": w.nondegeneracy.model_dump(mode="json"),
    }
  w2 = worlds["mvp-w2-generator-v2"]["analyst"]
  w3 = worlds["mvp-w3-generator-high-bg-ip-v2"]["analyst"]
  return {
    "seed": seed, "n": N, "baseline": base,
    "baseline_structural_valid": structural_valid(baseline),
    "baseline_duplicate_claim_invariant": _duplicate_control(base_tables, base, None),
    "family_sha256": family.sha256(), "worlds": worlds,
    "background_risk_sensitivity_pass": w3["n_ip_beneficiaries"] > w2["n_ip_beneficiaries"],
    "known_truth": _known_truth(seed),
  }


def build_report() -> dict[str, Any]:
  if _git("status", "--porcelain", "--untracked-files=no"):
    raise RuntimeError("producer checkout must be clean and committed")
  producer = _git("rev-parse", "HEAD")
  if _git("diff", "--name-only", "7af24e5", "--", "reports/phase5", "src/medicare_synth/fixtures/evidence_corpus", "src/medicare_synth/fixtures/evidence_ir"):
    raise RuntimeError("historical reports or frozen corpus differ from audited base")
  corpus, corpus_path = load_default_corpus()
  errors = verify_corpus_checksums(corpus)
  if errors:
    raise RuntimeError("corpus checksums failed: " + "; ".join(errors))
  tracked_reports = _git("ls-files", "reports").splitlines()
  historical = {path: _hash(ROOT / path) for path in tracked_reports}
  files = (
    "scripts/phase6_evaluate_v1.py", "src/medicare_synth/phase6.py",
    "src/medicare_synth/calibration.py", "src/medicare_synth/evidence_ir.py",
    "src/medicare_synth/evidence_corpus.py", "src/medicare_synth/worlds.py",
    "src/medicare_synth/synthesis.py", "src/medicare_synth/evaluation.py",
  )
  runs: list[dict[str, Any]] = []
  for seed in SEEDS:
    try:
      runs.append(_run_seed(seed, corpus, corpus_path))
    except ValueError as exc:
      runs.append({"seed": seed, "n": N, "error": f"{type(exc).__name__}: {exc}"})
  engine = all(
    "error" not in r and r["baseline_structural_valid"] and all(
      w["structural_valid"] and w["calibration_n_missing"] == 0
      and tuple(row["finding_id"] for row in w["calibration_targets"]) == corpus.finding_ids(PartitionName.CALIBRATION)
      and (w["weight_key"] is None or w["solver"]["converged"])
      for w in r["worlds"].values()
    ) for r in runs
  )
  utility = all(
    "error" not in r and r["baseline"]["n_eligible"] == N and r["baseline_duplicate_claim_invariant"]
    and r["background_risk_sensitivity_pass"] and r["known_truth"]["structural_valid"]
    and all(check["pass"] for check in r["known_truth"]["checks"].values())
    and all(w["analyst"]["n_eligible"] == N and w["duplicate_claim_invariant"] for w in r["worlds"].values())
    for r in runs
  )
  historical_summary = json.loads((ROOT / "reports/phase5/world_family_summary.json").read_text())
  freeze = load_evaluation_freeze(corpus=corpus)
  freeze_hash = hashlib.sha256(json.dumps(
    freeze.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
  ).encode()).hexdigest()
  return {
    "report_version": "phase6-engineering-evaluation-v1",
    "run_id": f"phase6-v1-{producer[:12]}",
    "evaluation_freeze_id": freeze.freeze_id,
    "evaluation_freeze_sha256": freeze_hash,
    "protocol_sha256": _hash(PROTOCOL), "producer_commit": producer,
    "code_sha256": {path: _hash(ROOT / path) for path in files},
    "environment": {
      "python": sys.version.split()[0], "uv_lock_sha256": _hash(ROOT / "uv.lock"),
      "polars": importlib.metadata.version("polars"), "pydantic": importlib.metadata.version("pydantic"),
      "pyarrow": importlib.metadata.version("pyarrow"),
    },
    "corpus_id": corpus.corpus_id, "corpus_sha256": _hash(corpus_path),
    "finding_hashes": {e.finding_id: e.sha256 for e in corpus.entries},
    "partition_ids": {p.value: list(corpus.finding_ids(p)) for p in PartitionName},
    "context": corpus.context_id, "seeds": list(SEEDS), "n": N,
    "historical_report_sha256": historical,
    "historical_phase5": {
      "producer_commit": "7673670", "family_id": historical_summary["family_id"],
      "family_sha256": historical_summary["family_sha256"],
      "worlds": [{"world_id": w["world_id"], "calibration_mae_after": w["calibration_mae_after"],
                  "holdout_mae": w["holdout_mae"]} for w in historical_summary["worlds"]],
      "comparison_note": "Historical N=6000 seed=42; protocol runs use N=2000 and are not byte-equivalent.",
    },
    "runs": runs,
    "disposition": {
      "engineering": "conditional-go" if engine else "no-go",
      "engineering_condition": "Conditional on independently replaying this exact report and passing the full verification suite.",
      "workflow_utility": "conditional-go" if utility else "no-go",
      "independent_fidelity": "no-go / insufficient evidence",
      "reason": "Andes women holdout was exposed; same paper supplies the Andes example fit. No fresh compatible human-approved independent evidence was supplied.",
      "release": "no-go without human approval and independent compatible evidence",
    },
    "limitations": ["Synthetic engineering evidence is not a Medicare finding.",
                    "Numerical solver tolerance is not an evidence-agreement threshold.",
                    "Prior holdout exposure and same-source overlap preclude independent validation."],
  }


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--output", type=Path, required=True, help="new report path; existing files are never overwritten")
  args = parser.parse_args()
  path = args.output.resolve()
  if path.exists() or path.is_relative_to((ROOT / "reports/phase5").resolve()):
    parser.error("output must be a new file outside historical reports/phase5")
  report = build_report()
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
  print(f"wrote {path}; sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
