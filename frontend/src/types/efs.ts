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

export interface EFSRequestPayload {
  methodology_version?: string
  raw_variables?: Record<string, any>
  statement_flags?: Record<string, boolean>
  ratio_output?: Record<string, any>
  feature_output?: Record<string, any>
}
