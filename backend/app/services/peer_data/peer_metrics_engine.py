"""Peer Metrics & Benchmark Engine for EFS™ Phase 6C.

Computes statistical benchmarks (median, mean, percentile rank, deviation) across a set
of selected peer companies.
Enforces minimum peer count protection (peer_count >= 3 required).
"""

import statistics
from typing import List, Optional
from pydantic import BaseModel
from app.services.peer_data.peer_selection_engine import PeerSelectionResult


class PeerMetricBenchmark(BaseModel):
    metric_key: str
    metric_label: str
    company_value: Optional[float]
    unit: str
    peer_median: Optional[float]
    peer_mean: Optional[float]
    peer_min: Optional[float]
    peer_max: Optional[float]
    peer_count: int
    percentile_rank: Optional[float]
    deviation_from_median: Optional[float]
    benchmark_status: str  # VERIFIED, INSUFFICIENT_PEERS, EXTERNAL_DATA_UNAVAILABLE
    provenance_source: str
    provenance_url: str


class PeerMetricsEngine:
    """Computes benchmark statistics over selected peer sets."""

    @staticmethod
    def compute_metric_benchmark(
        metric_key: str,
        metric_label: str,
        company_value: Optional[float],
        unit: str,
        peers: List[PeerSelectionResult],
        value_extractor_func,
        source_name: str = "Public Annual Reports & Exchange Disclosures",
        source_url: str = "https://www.bseindia.com",
    ) -> PeerMetricBenchmark:
        # Extract values from selected peers
        peer_values: List[float] = []
        for p in peers:
            if p.selected and p.candidate:
                val = value_extractor_func(p.candidate)
                if val is not None:
                    peer_values.append(float(val))

        peer_count = len(peer_values)

        if company_value is None:
            return PeerMetricBenchmark(
                metric_key=metric_key,
                metric_label=metric_label,
                company_value=None,
                unit=unit,
                peer_median=None,
                peer_mean=None,
                peer_min=None,
                peer_max=None,
                peer_count=peer_count,
                percentile_rank=None,
                deviation_from_median=None,
                benchmark_status="EXTERNAL_DATA_UNAVAILABLE",
                provenance_source=source_name,
                provenance_url=source_url,
            )

        if peer_count < 3:
            return PeerMetricBenchmark(
                metric_key=metric_key,
                metric_label=metric_label,
                company_value=company_value,
                unit=unit,
                peer_median=None,
                peer_mean=None,
                peer_min=None,
                peer_max=None,
                peer_count=peer_count,
                percentile_rank=None,
                deviation_from_median=None,
                benchmark_status="INSUFFICIENT_PEERS",
                provenance_source=source_name,
                provenance_url=source_url,
            )

        peer_values_sorted = sorted(peer_values)
        peer_median = round(float(statistics.median(peer_values_sorted)), 2)
        peer_mean = round(float(statistics.mean(peer_values_sorted)), 2)
        peer_min = round(float(peer_values_sorted[0]), 2)
        peer_max = round(float(peer_values_sorted[-1]), 2)
        deviation = round(float(company_value - peer_median), 2)

        # Calculate percentile rank
        below_count = sum(1 for v in peer_values_sorted if v < company_value)
        equal_count = sum(1 for v in peer_values_sorted if v == company_value)
        percentile = round(((below_count + 0.5 * equal_count) / peer_count) * 100.0, 1)

        return PeerMetricBenchmark(
            metric_key=metric_key,
            metric_label=metric_label,
            company_value=round(float(company_value), 2),
            unit=unit,
            peer_median=peer_median,
            peer_mean=peer_mean,
            peer_min=peer_min,
            peer_max=peer_max,
            peer_count=peer_count,
            percentile_rank=percentile,
            deviation_from_median=deviation,
            benchmark_status="VERIFIED",
            provenance_source=source_name,
            provenance_url=source_url,
        )
