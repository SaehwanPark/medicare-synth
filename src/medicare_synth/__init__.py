"""Medicare-Synth package root.

Provenance-backed contemporary Medicare synthetic data and research fixtures.
"""

__version__ = "0.1.0"

from medicare_synth.evidence import RKBEvidenceSnapshot, VariableContract
from medicare_synth.expansion import HorizontalExpander, TabDatSynthAdapter, VerticalExpander
from medicare_synth.manifest import FileManifest, SourceManifest
from medicare_synth.models import ProvenanceStatus
from medicare_synth.normalizer import BaselineNormalizer
from medicare_synth.release import FidelityProfile, ReleaseExporter, ReleaseManifest
from medicare_synth.scenarios import ScenarioCompiler
from medicare_synth.validation import Finding, FindingCategory, RelationalValidator, Severity, ValidationReport

__all__ = [
  "BaselineNormalizer",
  "FidelityProfile",
  "FileManifest",
  "Finding",
  "FindingCategory",
  "HorizontalExpander",
  "ProvenanceStatus",
  "RKBEvidenceSnapshot",
  "RelationalValidator",
  "ReleaseExporter",
  "ReleaseManifest",
  "ScenarioCompiler",
  "Severity",
  "SourceManifest",
  "TabDatSynthAdapter",
  "ValidationReport",
  "VariableContract",
  "VerticalExpander",
]
