"""Medicare-Synth package root.

Provenance-backed contemporary Medicare synthetic data and research fixtures.
"""

__version__ = "0.1.0"

from medicare_synth.audit import AuditEngine, AuditReport, ColumnAuditMetric, KAnonymityResult
from medicare_synth.catalog import ScenarioCatalog, ScenarioEntry
from medicare_synth.diff import DiffReport, SchemaDiffer
from medicare_synth.evidence import RKBEvidenceSnapshot, VariableContract
from medicare_synth.expansion import HorizontalExpander, TabDatSynthAdapter, VerticalExpander
from medicare_synth.manifest import FileManifest, SourceManifest
from medicare_synth.models import (
  BeneficiaryRecord,
  CarrierClaimLineRecord,
  DurableMedicalEquipmentClaimRecord,
  HomeHealthAgencyClaimRecord,
  HospiceClaimHeaderRecord,
  InpatientClaimHeaderRecord,
  MBSFChronicConditionsRecord,
  MBSFCostAndUseRecord,
  MBSFPartDRecord,
  OutpatientClaimHeaderRecord,
  PrescriptionDrugEventRecord,
  ProvenanceStatus,
  SkilledNursingFacilityClaimRecord,
)
from medicare_synth.normalizer import BaselineNormalizer
from medicare_synth.profile import LimitationsProfile, LimitationsProfiler
from medicare_synth.release import FidelityProfile, ReleaseExporter, ReleaseManifest
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import Finding, FindingCategory, RelationalValidator, Severity, ValidationReport

__all__ = [
  "AuditEngine",
  "AuditReport",
  "BaselineNormalizer",
  "BeneficiaryRecord",
  "CarrierClaimLineRecord",
  "ColumnAuditMetric",
  "DiffReport",
  "DurableMedicalEquipmentClaimRecord",
  "FidelityProfile",
  "FileManifest",
  "Finding",
  "FindingCategory",
  "HomeHealthAgencyClaimRecord",
  "HorizontalExpander",
  "HospiceClaimHeaderRecord",
  "InpatientClaimHeaderRecord",
  "KAnonymityResult",
  "LimitationsProfile",
  "LimitationsProfiler",
  "MBSFChronicConditionsRecord",
  "MBSFCostAndUseRecord",
  "MBSFPartDRecord",
  "OutpatientClaimHeaderRecord",
  "PrescriptionDrugEventRecord",
  "ProvenanceStatus",
  "RKBEvidenceSnapshot",
  "RelationalValidator",
  "ReleaseExporter",
  "ReleaseManifest",
  "ScenarioCatalog",
  "ScenarioCompiler",
  "ScenarioEntry",
  "SchemaDiffer",
  "Severity",
  "SkilledNursingFacilityClaimRecord",
  "SourceManifest",
  "TabDatSynthAdapter",
  "ValidationReport",
  "VariableContract",
  "VerticalExpander",
]
