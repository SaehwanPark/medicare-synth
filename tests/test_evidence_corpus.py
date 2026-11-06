"""Behavioral tests for Phase 3 evidence corpus freeze."""

from __future__ import annotations

import pytest

from medicare_synth.evidence_corpus import (
  CORPUS_SCHEMA_VERSION,
  CorpusError,
  EvidenceCorpus,
  PartitionName,
  assert_active_partition_support,
  default_mvp_corpus_path,
  ensure_corpus_checksums,
  execute_partition,
  freeze_corpus,
  load_corpus,
  load_corpus_finding,
  package_corpus_dir,
  replace_entry,
  verify_corpus_checksums,
)
from medicare_synth.evidence_ir import EvidenceRole, package_fixtures_dir
from medicare_synth.synthesis import (
  ConditionalWorldParams,
  generate_diabetes_ip_world,
)


@pytest.fixture(scope="module")
def corpus() -> EvidenceCorpus:
  path = default_mvp_corpus_path()
  assert path.is_file()
  return load_corpus(path)


def test_corpus_schema_and_freeze_metadata(corpus: EvidenceCorpus) -> None:
  assert corpus.schema_version == CORPUS_SCHEMA_VERSION
  assert corpus.corpus_id == "mvp-2021-om-ffs-diabetes-ip-corpus-v1"
  assert corpus.frozen is True
  assert corpus.reviewer == "phase3-corpus-freeze"
  assert len(corpus.finding_ids(PartitionName.CALIBRATION)) == 3
  assert len(corpus.finding_ids(PartitionName.HOLDOUT)) == 1
  assert len(corpus.finding_ids(PartitionName.DIAGNOSTIC)) >= 2
  assert len(corpus.finding_ids(PartitionName.EXCLUDED)) >= 2


def test_checksums_verify(corpus: EvidenceCorpus) -> None:
  assert verify_corpus_checksums(corpus) == []
  ensure_corpus_checksums(corpus)


def test_active_partitions_supported(corpus: EvidenceCorpus) -> None:
  assert assert_active_partition_support(corpus) == []


def test_frozen_corpus_refuses_mutation(corpus: EvidenceCorpus) -> None:
  entry = corpus.entries[0]
  with pytest.raises(CorpusError, match="frozen"):
    replace_entry(corpus, entry)
  with pytest.raises(CorpusError, match="already frozen"):
    freeze_corpus(
      corpus,
      frozen_at="2099-01-01",
      reviewer="x",
      rationale="nope",
    )


def test_holdout_sex_stratum_filters_women(corpus: EvidenceCorpus) -> None:
  finding = load_corpus_finding(
    corpus, "lit03-mmwr-diabetes-prev-2015-women"
  )
  assert finding.role == EvidenceRole.HOLDOUT
  assert finding.population.sex_codes == ("2",)
  world = generate_diabetes_ip_world(
    ConditionalWorldParams(
      n_beneficiaries=3000,
      seed=21,
      diabetes_prevalence=0.30,
      p_ip_given_diabetes=0.15,
      p_ip_given_no_diabetes=0.05,
    )
  )
  reports = execute_partition(
    corpus, PartitionName.HOLDOUT, world.tables()
  )
  assert len(reports) == 1
  report = reports[0]
  assert report.executable is True
  assert report.n_eligible > 0
  # Women are roughly half of a 48/52 sex split world.
  assert report.n_eligible < world.params.n_beneficiaries


def test_calibration_partition_executes(corpus: EvidenceCorpus) -> None:
  world = generate_diabetes_ip_world(
    ConditionalWorldParams(
      n_beneficiaries=4000,
      seed=5,
      diabetes_prevalence=0.277,
      p_ip_given_diabetes=0.13,
      p_ip_given_no_diabetes=0.06,
      hf_prevalence=0.12,
    )
  )
  reports = execute_partition(
    corpus, PartitionName.CALIBRATION, world.tables()
  )
  assert len(reports) == 3
  assert all(r.executable for r in reports)
  by_id = {r.finding_id: r for r in reports}
  assert by_id["cms-agg03-diabetes-prev-ffs-2018"].synthetic_estimate == pytest.approx(
    0.277, abs=0.05
  )
  assert by_id["cms-agg04-hf-prev-ffs-2022"].synthetic_estimate == pytest.approx(
    0.12, abs=0.05
  )
  assert by_id["lit07-avalere-ffs-diabetes-ip-risk"].synthetic_estimate == pytest.approx(
    0.13, abs=0.05
  )


def test_excluded_partition_refuses_execute(corpus: EvidenceCorpus) -> None:
  world = generate_diabetes_ip_world(
    ConditionalWorldParams(
      n_beneficiaries=100,
      seed=1,
      diabetes_prevalence=0.3,
      p_ip_given_diabetes=0.1,
      p_ip_given_no_diabetes=0.05,
    )
  )
  with pytest.raises(CorpusError, match="excluded"):
    execute_partition(corpus, PartitionName.EXCLUDED, world.tables())


def test_checksum_tamper_detected(corpus: EvidenceCorpus, tmp_path) -> None:
  # Copy fixtures tree and mutate one finding byte.
  import shutil

  src_root = package_fixtures_dir().parent
  dst_root = tmp_path / "fixtures"
  shutil.copytree(src_root, dst_root)
  target = dst_root / "evidence_ir" / "cms_agg03_diabetes_prev_ffs_2018.json"
  text = target.read_text(encoding="utf-8")
  target.write_text(text.replace("0.277", "0.278"), encoding="utf-8")
  errors = verify_corpus_checksums(corpus, fixtures_root=dst_root)
  assert any("cms-agg03-diabetes-prev-ffs-2018" in e for e in errors)


def test_package_corpus_dir_layout() -> None:
  assert package_corpus_dir().is_dir()
  assert default_mvp_corpus_path().is_file()
