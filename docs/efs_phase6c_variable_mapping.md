# EFS™ PHASE 6C — EXTERNAL VARIABLE MAPPING & PROVENANCE SPECIFICATION

This specification defines how the 5 external context variables receive supporting peer and regulatory evidence.

| EFS Variable | Metric Name | Benchmark Calculation | Provenance Data Fields Captured | Fallback Status |
|---|---|---|---|---|
| **FSQ10** | Effective Tax Rate Anomaly | Peer Median ETR, Percentile Rank, ETR Deviation | `company_etr`, `peer_median_etr`, `peer_count`, `source_url`, `retrieved_at` | `EXTERNAL_DATA_UNAVAILABLE` |
| **GD04** | Audit Tenure / Rotation | Audit Firm Name, Tenure Years, Peer Rotation Events | `auditor_name`, `tenure_years`, `peer_rotation_count`, `source_doc` | `EXTERNAL_DATA_UNAVAILABLE` |
| **GD06** | Promoter Share Pledge | Promoter Pledge %, Peer Median Pledge % | `promoter_pledge_pct`, `peer_median_pledge_pct`, `disclosure_date`, `source` | `EXTERNAL_DATA_UNAVAILABLE` |
| **GD09** | Regulatory Enforcement | Official Regulatory Orders, Exchange Disclosures | `authority`, `event_type`, `description`, `source_url`, `status` | `NOT_FOUND` / `SOURCE_UNAVAILABLE` |
| **GS08** | Earnings Persistence | Multi-year Operating Earnings Series, Persistence Check | `operating_earnings_series`, `years_available`, `persistence_status` | `INSUFFICIENT_HISTORY` |
