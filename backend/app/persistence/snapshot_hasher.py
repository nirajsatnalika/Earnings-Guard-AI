"""Deterministic canonical snapshot hasher for EFS™ forensic audit integrity.

Note: _build_result_dict_for_hashing is defined in assessment_repository to avoid circular imports.
The router imports it from there.

Produces SHA-256 hashes over canonical JSON serializations of:
- input_snapshot_hash: the raw input payload submitted to the EFS engine
- assessment_snapshot_hash: the deterministic EFS assessment result

CRITICAL DESIGN RULES:
- Hashes are generated server-side only.
- Hashes are immutable once created. Never recomputed after storage.
- Hashes are AUDIT/INTEGRITY metadata ONLY.
- They do NOT alter EFS scores, pillar weights, rule severities, or any calculation.
- They do NOT affect calibration logic.
- Their sole purpose is to verify that a stored snapshot has not changed since creation.
"""

import hashlib
import json
from typing import Any, Dict


def _canonical_serialize(obj: Any) -> str:
    """Produce a deterministic canonical JSON string.

    Rules:
    - Keys sorted recursively (sort_keys=True)
    - No whitespace (separators=(',', ':'))
    - None values preserved (not stripped)
    - Floats serialized as-is (Python default repr)
    - Unicode encoded as UTF-8

    This ensures that two identical objects always produce identical output
    regardless of insertion order.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def hash_input_snapshot(input_payload: Dict[str, Any]) -> str:
    """Generate SHA-256 hex digest of the canonical input payload.

    Args:
        input_payload: The raw input dict submitted to EFSEngine.run()

    Returns:
        64-character lowercase SHA-256 hex string.
    """
    canonical = _canonical_serialize(input_payload)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def hash_assessment_snapshot(assessment_dict: Dict[str, Any]) -> str:
    """Generate SHA-256 hex digest of the canonical assessment result.

    The assessment_dict should include all deterministic fields:
    overall score/status, pillar scores, variable scores, model results,
    forensic findings, confidence, and audit trail.

    Args:
        assessment_dict: Dict representation of EFSExecutionResult.

    Returns:
        64-character lowercase SHA-256 hex string.
    """
    canonical = _canonical_serialize(assessment_dict)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def verify_snapshot_integrity(stored_hash: str, current_dict: Dict[str, Any]) -> bool:
    """Verify that a stored snapshot hash matches a freshly serialized dict.

    Used for audit verification only. Does NOT alter assessment data.

    Args:
        stored_hash: The SHA-256 hex string stored in the DB at assessment creation.
        current_dict: The dict to hash and compare against.

    Returns:
        True if hashes match (snapshot unmodified), False otherwise.
    """
    current_hash = hash_assessment_snapshot(current_dict)
    return stored_hash == current_hash
