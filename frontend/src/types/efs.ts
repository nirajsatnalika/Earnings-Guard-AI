export type DataQualityLevel = 'HIGH' | 'MEDIUM' | 'LOW' | 'INSUFFICIENT'
export type ModelRole = 'Supporting Evidence' | 'Cross-Validation'
export type RuleSeverity = 'Critical' | 'High' | 'Medium' | 'Low' | 'Context'
export type EvidenceState = 'Triggered' | 'Not Triggered' | 'Not Evaluated' | 'Not Applicable' | 'Insufficient Evidence'

export interface EFSVariable {
  variable_id: string
  variable_name: string
  pillar: string
  raw_value: number | null
  unit: string
  score: number | null
  scoring_band: string | null
  data_status: 'AVAILABLE' | 'MISSING' | 'NOT_APPLICABLE' | 'INSUFFICIENT_EVIDENCE'
  source_fields: string[]
  calculation_status: string
}

export interface PillarResult {
  pillar_id: string
  pillar_name: string
  pillar_score: number | null
  variables_evaluated: number
  variables_available: number
  variables_missing: string[]
  key_positive_drivers: string[]
  key_negative_drivers: string[]
  data_quality: DataQualityLevel
  status: 'COMPLETED' | 'INELIGIBLE' | 'CALIBRATION_PENDING'
  variables: EFSVariable[]
}

export interface EstablishedModel {
  model_id: string
  model_name: string
  specification?: string
  score: number | null
  threshold?: number
  max_score?: number
  zone?: string
  risk_signal: string
  role: ModelRole
  status: string
  interpretation: string
  components?: Record<string, any>
  signals?: Record<string, any>
}

export interface EstablishedModels {
  beneish_m_score: EstablishedModel
  sloan_accrual: EstablishedModel
  altman_z_score: EstablishedModel
  piotroski_f_score: EstablishedModel
  ohlson_o_score: EstablishedModel
}

export interface ForensicFinding {
  rule_id: string
  rule_name: string
  pillar: string
  triggered: boolean
  severity: RuleSeverity
  trigger_condition: string
  evidence: string
  forensic_finding: string
  why_it_matters: string
  recommended_investigation: string
  question_for_management: string
  evidence_state: EvidenceState
}

export interface AuditTrail {
  assessment_id: string
  analysis_id: string
  efs_version: string
  scoring_version: string
  rulebook_version: string
  engine_version: string
  timestamp: string
  variables_evaluated: number
  variables_available: number
  rules_evaluated: number
  rules_triggered: number
  calculation_time_ms: number
}

export interface OverallAssessment {
  score: number | null
  score_status: 'CALIBRATION_PENDING' | 'COMPLETED'
  risk_level: string | null
  confidence: number
}

export interface EFSResponse {
  assessment_id: string
  analysis_id: string
  company_name?: string
  ticker?: string
  efs_version: string
  status: string
  overall: OverallAssessment
  pillars: PillarResult[]
  established_models: EstablishedModels
  forensic_findings: ForensicFinding[]
  red_flags: string[]
  management_questions: string[]
  limitations: string[]
  audit_trail: AuditTrail
}

export interface KeyFindingNarrative {
  rule_id?: string
  title: string
  what_observed: string
  why_it_matters: string
  supporting_evidence: string
  legitimate_explanations: string[]
  investigation_next_steps: string
  evidence_refs: string[]
}

export interface PillarNarrative {
  pillar_id: string
  pillar_name: string
  summary: string
  positive_signals: string[]
  adverse_signals: string[]
  missing_evidence: string[]
  investigation_areas: string[]
}

export interface ModelInterpretation {
  model_id: string
  model_name: string
  meaning: string
  role_in_efs: string
  limitations: string
}

export interface CrossSignalAnalysisItem {
  theme: string
  converging_signals: string[]
  explanation: string
  cited_variables: string[]
  cited_rules: string[]
}

export interface EFSNarrativeResponse {
  narrative_version: string
  analysis_id: string
  assessment_id: string
  generated_at: string
  executive_summary: string
  overall_interpretation: string
  key_findings: KeyFindingNarrative[]
  pillar_narratives: PillarNarrative[]
  model_interpretations: ModelInterpretation[]
  cross_signal_analysis: CrossSignalAnalysisItem[]
  investigation_priorities: Record<string, any>[]
  management_questions_context: Record<string, any>[]
  data_limitations: string[]
  methodology_note: string
  disclaimer: string
  provider_info: {
    provider: string
    model: string
    fallback_used: boolean
  }
}

export interface EFSRequestPayload {
  methodology_version?: string
  raw_variables?: Record<string, any>
  statement_flags?: Record<string, boolean>
  ratio_output?: Record<string, any>
  feature_output?: Record<string, any>
}

export interface AssessmentListItem {
  id: string
  analysis_id: string
  company_id: string
  assessment_status: 'DRAFT' | 'RUNNING' | 'COMPLETED' | 'FAILED'
  score_status: 'CALIBRATION_PENDING' | 'COMPLETED'
  overall_score: number | null
  risk_level: string | null
  confidence_score: number | null
  confidence_level: string | null
  rules_triggered: number | null
  variables_evaluated: number | null
  efs_version: string
  methodology_version: string
  created_at: string
  completed_at: string | null
  input_snapshot_hash: string | null
  assessment_snapshot_hash: string | null
}

export interface AssessmentListResponse {
  items: AssessmentListItem[]
  total: number
  page: number
  limit: number
}

export interface CompanyRecord {
  id: string
  legal_name: string
  display_name: string | null
  ticker: string | null
  exchange: string | null
  country: string | null
  industry: string | null
  created_at: string
  updated_at: string
}

export interface CompanyCreateRequest {
  legal_name: string
  display_name?: string
  ticker?: string
  exchange?: string
  country?: string
  industry?: string
}

