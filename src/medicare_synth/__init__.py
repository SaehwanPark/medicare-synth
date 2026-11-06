"""Medicare-Synth package root.

Provenance-backed contemporary Medicare synthetic data and research fixtures.
"""

__version__ = "0.1.0"

from medicare_synth.audit import (
    AuditEngine,
    AuditReport,
    ColumnAuditMetric,
    KAnonymityResult,
)
from medicare_synth.catalog import ScenarioCatalog, ScenarioEntry
from medicare_synth.diff import DiffReport, SchemaDiffer
from medicare_synth.evidence import (
    EvidenceSource,
    RKBEvidenceSnapshot,
    VariableContract,
)
from medicare_synth.evidence_ir import (
    SCHEMA_VERSION as EVIDENCE_IR_SCHEMA_VERSION,
    ComparisonReport,
    CompatibilityReport,
    CompiledFinding,
    EvidenceIRError,
    FindingIR,
    comparison_to_dict,
    compile_finding,
    draft_finding_from_fields,
    ensure_valid,
    execute_finding,
    load_finding,
    package_fixtures_dir,
    parse_finding,
    validate_finding,
)
from medicare_synth.expansion import (
    HorizontalExpander,
    TabDatSynthAdapter,
    VerticalExpander,
)
from medicare_synth.synthesis import (
    ConditionalWorld,
    ConditionalWorldEstimates,
    ConditionalWorldParams,
    estimate_world_relationships,
    generate_diabetes_ip_world,
    relationships_within_tolerance,
    split_bene_ids,
    unique_support_ratio,
)
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
    MBSFBaseEnrollmentRecord,
    MBSFOtherChronicConditionsRecord,
    MBSFNDIRecord,
    MBSFRiskAdjustmentRecord,
    MBSFPartCRecord,
    OutpatientClaimHeaderRecord,
    PrescriptionDrugEventRecord,
    ProvenanceStatus,
    SkilledNursingFacilityClaimRecord,
)
from medicare_synth.normalizer import BaselineNormalizer
from medicare_synth.profile import LimitationsProfile, LimitationsProfiler
from medicare_synth.puf import PufImportError, PufImporter, PufSlice
from medicare_synth.release import FidelityProfile, ReleaseExporter, ReleaseManifest
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import (
    Finding,
    FindingCategory,
    RelationalValidator,
    Severity,
    ValidationReport,
)
from medicare_synth.workflow import run_autonomous_workflow

__all__ = [
    "AuditEngine",
    "AuditReport",
    "BaselineNormalizer",
    "BeneficiaryRecord",
    "CarrierClaimLineRecord",
    "ColumnAuditMetric",
    "ConditionalWorld",
    "ConditionalWorldEstimates",
    "ConditionalWorldParams",
    "DiffReport",
    "EVIDENCE_IR_SCHEMA_VERSION",
    "EvidenceIRError",
    "EvidenceSource",
    "ComparisonReport",
    "CompatibilityReport",
    "CompiledFinding",
    "FindingIR",
    "comparison_to_dict",
    "compile_finding",
    "draft_finding_from_fields",
    "ensure_valid",
    "estimate_world_relationships",
    "execute_finding",
    "generate_diabetes_ip_world",
    "load_finding",
    "package_fixtures_dir",
    "parse_finding",
    "validate_finding",
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
    "PufImportError",
    "PufImporter",
    "PufSlice",
    "MBSFBaseEnrollmentRecord",
    "MBSFChronicConditionsRecord",
    "MBSFCostAndUseRecord",
    "MBSFNDIRecord",
    "MBSFOtherChronicConditionsRecord",
    "MBSFPartCRecord",
    "MBSFPartDRecord",
    "MBSFRiskAdjustmentRecord",
    "OutpatientClaimHeaderRecord",
    "PrescriptionDrugEventRecord",
    "ProvenanceStatus",
    "RKBEvidenceSnapshot",
    "RelationalValidator",
    "relationships_within_tolerance",
    "ReleaseExporter",
    "ReleaseManifest",
    "run_autonomous_workflow",
    "ScenarioCatalog",
    "ScenarioCompiler",
    "ScenarioEntry",
    "SchemaDiffer",
    "Severity",
    "SkilledNursingFacilityClaimRecord",
    "SourceManifest",
    "split_bene_ids",
    "TabDatSynthAdapter",
    "unique_support_ratio",
    "ValidationReport",
    "VariableContract",
    "VerticalExpander",
]
