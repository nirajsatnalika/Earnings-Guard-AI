"""Forensic narrative provider abstraction and deterministic fallback implementation."""

import json
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List

from app.ai.prompts import SYSTEM_PROMPT, build_evidence_prompt_payload
from app.ai.schemas import (
    CrossSignalAnalysisItem,
    EFSNarrativeResponse,
    KeyFindingNarrative,
    ModelInterpretation,
    PillarNarrative,
)

logger = logging.getLogger(__name__)


class ForensicNarrativeProvider(ABC):
    """Abstract base class for AI Forensic Narrative generation providers."""

    @abstractmethod
    async def generate_narrative(
        self, analysis_id: str, assessment_dict: Dict[str, Any]
    ) -> EFSNarrativeResponse:
        """Generate structured narrative for given assessment payload."""
        pass


def _get_val(obj: Any, key: str, default: Any = None) -> Any:
    """Extract key/attribute safely from dict or object."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


class FallbackNarrativeProvider(ForensicNarrativeProvider):
    """Deterministic rule-based narrative synthesizer used as a fallback when LLM APIs are unavailable."""

    async def generate_narrative(
        self, analysis_id: str, assessment_dict: Dict[str, Any]
    ) -> EFSNarrativeResponse:
        logger.info("Synthesizing deterministic fallback AI narrative for analysis_id=%s", analysis_id)

        assessment_id = _get_val(assessment_dict, "assessment_id", "N/A")
        overall = _get_val(assessment_dict, "overall", {})
        pillars = _get_val(assessment_dict, "pillars", [])
        models = _get_val(assessment_dict, "established_models", {})
        findings = _get_val(assessment_dict, "forensic_findings", [])
        red_flags = _get_val(assessment_dict, "red_flags", [])
        management_questions = _get_val(assessment_dict, "management_questions", [])
        limitations = _get_val(assessment_dict, "limitations", [])

        # 1. Executive Summary Synthesis
        if red_flags:
            exec_summary = (
                f"The assessment evaluated deterministic financial indicators for {analysis_id}. "
                f"It identified {len(red_flags)} forensic red flag(s) and {len(findings)} triggered rule finding(s) requiring investigation. "
                "The strongest adverse signals relate to financial quality metrics and disclosure completeness. "
                "These signals require corroboration through detailed customer/vendor verification and audit procedures."
            )
        else:
            exec_summary = (
                f"The assessment evaluated deterministic financial indicators for {analysis_id}. "
                "No critical forensic red flags were triggered across available financial statements. "
                "Continued monitoring is recommended as additional disclosure data becomes available."
            )

        # 2. Overall Interpretation
        overall_interp = (
            "The deterministic analysis across seven pillars is complete. "
            "Underlying variables and forensic rules have been evaluated. "
            "The overall composite EFS™ weighted score is intentionally CALIBRATION PENDING. "
            "This assessment must be interpreted through its individual pillar evidence, established model indicators, "
            "and specific forensic rule findings rather than a single composite score."
        )

        # 3. Key Findings
        key_findings_list: List[KeyFindingNarrative] = []
        for f in findings[:5]:  # Top 5 findings
            r_id = _get_val(f, "rule_id")
            r_name = _get_val(f, "rule_name", "Forensic Finding")
            evidence = _get_val(f, "evidence", "Trigger condition observed in statements.")
            why_m = _get_val(f, "why_it_matters", "Indicates potential financial reporting quality anomaly.")
            sev = _get_val(f, "severity", "Medium")
            f_finding = _get_val(f, "forensic_finding", "")
            rec_inv = _get_val(f, "recommended_investigation", "Perform transaction sampling and audit verification.")

            key_findings_list.append(
                KeyFindingNarrative(
                    rule_id=r_id,
                    title=r_name,
                    what_observed=evidence,
                    why_it_matters=why_m,
                    supporting_evidence=f"Rule {r_id} ({sev} severity): {f_finding}",
                    legitimate_explanations=[
                        "Business expansion or change in operational mix.",
                        "One-off non-recurring accounting transaction or classification adjustment.",
                    ],
                    investigation_next_steps=rec_inv,
                    evidence_refs=[r_id] if r_id else [],
                )
            )

        # 4. Pillar Narratives
        pillar_narratives_list: List[PillarNarrative] = []
        for p in pillars:
            p_name = _get_val(p, "pillar_name", _get_val(p, "pillar_id", ""))
            p_id = _get_val(p, "pillar_id", "")
            pos_drivers = _get_val(p, "key_positive_drivers", [])
            neg_drivers = _get_val(p, "key_negative_drivers", [])
            missing = _get_val(p, "variables_missing", [])
            vars_eval = _get_val(p, "variables_evaluated", 0)
            data_q = _get_val(p, "data_quality", "UNKNOWN")
            
            p_summary = f"Pillar '{p_name}' evaluated {vars_eval} variables. Data quality is rated as '{data_q}'."
            if neg_drivers:
                p_summary += f" Adverse indicators observed in {', '.join(neg_drivers[:3])}."
            else:
                p_summary += " No significant adverse indicators detected in available inputs."

            pillar_narratives_list.append(
                PillarNarrative(
                    pillar_id=p_id,
                    pillar_name=p_name,
                    summary=p_summary,
                    positive_signals=pos_drivers if isinstance(pos_drivers, list) else [],
                    adverse_signals=neg_drivers if isinstance(neg_drivers, list) else [],
                    missing_evidence=missing if isinstance(missing, list) else [],
                    investigation_areas=[f"Verify source schedules for {p_name} variables."],
                )
            )

        # 5. Established Model Interpretations
        model_interps_list: List[ModelInterpretation] = []
        model_names_map = {
            "beneish_m_score": ("MODEL01", "Beneish M-Score", "Supporting Evidence"),
            "sloan_accrual": ("MODEL02", "Sloan Accrual Model", "Supporting Evidence"),
            "altman_z_score": ("MODEL03", "Altman Z-Score", "Cross-Validation"),
            "piotroski_f_score": ("MODEL04", "Piotroski F-Score", "Cross-Validation"),
            "ohlson_o_score": ("MODEL05", "Ohlson O-Score", "Cross-Validation"),
        }
        for key, (m_id, m_name, m_role) in model_names_map.items():
            m_data = _get_val(models, key, {})
            status_str = _get_val(m_data, "status", "EVALUATED")
            score_val = _get_val(m_data, "score")
            interp_str = _get_val(m_data, "interpretation", "Model evaluated per methodology rules.")
            risk_sig = _get_val(m_data, "risk_signal", "Evaluated")

            if status_str == "INSUFFICIENT_DATA" or score_val is None:
                meaning_text = f"{m_name} could not be computed due to missing input components."
            else:
                meaning_text = f"{m_name} yielded a score of {score_val} ({risk_sig})."

            model_interps_list.append(
                ModelInterpretation(
                    model_id=m_id,
                    model_name=m_name,
                    meaning=meaning_text,
                    role_in_efs=m_role,
                    limitations=interp_str,
                )
            )
        # 6. Cross-Signal Analysis
        cross_signals_list: List[CrossSignalAnalysisItem] = []
        if len(findings) >= 2:
            cited_r = [_get_val(f, "rule_id", "") for f in findings[:3] if _get_val(f, "rule_id")]
            cross_signals_list.append(
                CrossSignalAnalysisItem(
                    theme="Financial Reporting Consistency & Accrual Alignment",
                    converging_signals=[_get_val(f, "rule_name", "") for f in findings[:3]],
                    explanation="Multiple independent forensic rules have triggered concurrently, indicating directional alignment in elevated reporting risk.",
                    cited_variables=[],
                    cited_rules=cited_r,
                )
            )

        # 7. Management Questions Context
        mq_context = [
            {
                "question": q,
                "forensic_context": "Designed to clarify underlying accounting policy, valuation assumptions, or period-end cut-off."
            }
            for q in management_questions
        ]

        # 8. Investigation Priorities Context
        inv_priorities = []
        for idx, f in enumerate(findings[:5], start=1):
            r_name = _get_val(f, "rule_name", "Forensic Item")
            sev = _get_val(f, "severity", "Medium")
            why_m = _get_val(f, "why_it_matters", "")
            rec_inv = _get_val(f, "recommended_investigation", "Inspect supporting ledger detail.")
            
            inv_priorities.append({
                "priority": idx,
                "area": r_name,
                "severity": sev,
                "why_matters": why_m,
                "suggested_procedures": [rec_inv],
            })

        return EFSNarrativeResponse(
            analysis_id=analysis_id,
            assessment_id=assessment_id,
            generated_at=datetime.utcnow().isoformat() + "Z",
            executive_summary=exec_summary,
            overall_interpretation=overall_interp,
            key_findings=key_findings_list,
            pillar_narratives=pillar_narratives_list,
            model_interpretations=model_interps_list,
            cross_signal_analysis=cross_signals_list,
            investigation_priorities=inv_priorities,
            management_questions_context=mq_context,
            data_limitations=limitations,
            provider_info={
                "provider": "deterministic-fallback",
                "model": "rule-based-synthesizer",
                "fallback_used": True,
            },
        )


class DefaultForensicNarrativeProvider(ForensicNarrativeProvider):
    """LLM Provider executing external API calls (e.g. OpenAI / Gemini) with automatic fallback."""

    def __init__(self, api_key: str, provider_name: str = "openai", model_name: str = "gpt-4o"):
        self.api_key = api_key
        self.provider_name = provider_name.lower()
        self.model_name = model_name
        self.fallback_provider = FallbackNarrativeProvider()

    async def generate_narrative(
        self, analysis_id: str, assessment_dict: Dict[str, Any]
    ) -> EFSNarrativeResponse:
        if not self.api_key:
            logger.warning("No API key configured for %s. Using deterministic fallback.", self.provider_name)
            return await self.fallback_provider.generate_narrative(analysis_id, assessment_dict)

        try:
            # Prepare evidence prompt with prompt injection defenses
            user_prompt = build_evidence_prompt_payload(assessment_dict)
            
            # If an LLM client library (openai/google.generativeai) is installed and key is set:
            if self.provider_name == "openai":
                import openai
                client = openai.AsyncOpenAI(api_key=self.api_key)
                completion = await client.chat.completions.create(
                    model=self.model_name,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,
                    timeout=15.0,
                )
                raw_json = completion.choices[0].message.content or "{}"
                data = json.loads(raw_json)
                data["analysis_id"] = analysis_id
                data["assessment_id"] = assessment_dict.get("assessment_id", "")
                data["provider_info"] = {
                    "provider": "openai",
                    "model": self.model_name,
                    "fallback_used": False,
                }
                return EFSNarrativeResponse.model_validate(data)

        except Exception as exc:
            logger.error("LLM Provider call failed (%s): %s. Falling back to deterministic narrative.", self.provider_name, exc)

        return await self.fallback_provider.generate_narrative(analysis_id, assessment_dict)


def get_narrative_provider() -> ForensicNarrativeProvider:
    """Factory creating configured narrative provider based on environment variables."""
    provider_type = os.getenv("AI_PROVIDER", "fallback").lower()
    openai_key = os.getenv("OPENAI_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    if provider_type == "openai" and openai_key:
        model = os.getenv("AI_MODEL", "gpt-4o")
        return DefaultForensicNarrativeProvider(api_key=openai_key, provider_name="openai", model_name=model)
    elif provider_type == "gemini" and gemini_key:
        model = os.getenv("AI_MODEL", "gemini-1.5-pro")
        return DefaultForensicNarrativeProvider(api_key=gemini_key, provider_name="gemini", model_name=model)

    return FallbackNarrativeProvider()
