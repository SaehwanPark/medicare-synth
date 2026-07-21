"""Medicare-Synth package root.

Provenance-backed contemporary Medicare synthetic data and research fixtures.
"""

__version__ = "0.1.0"

from medicare_synth.evidence import RKBEvidenceSnapshot, VariableContract
from medicare_synth.manifest import FileManifest, SourceManifest

__all__ = [
  "FileManifest",
  "SourceManifest",
  "RKBEvidenceSnapshot",
  "VariableContract",
]
