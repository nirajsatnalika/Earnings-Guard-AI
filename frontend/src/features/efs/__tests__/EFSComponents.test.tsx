import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AssessmentStatus } from '../components/AssessmentStatus'
import { CalibrationNotice } from '../components/CalibrationNotice'
import { PillarsOverview } from '../components/PillarsOverview'
import { EstablishedModelsPanel } from '../components/EstablishedModelsPanel'
import { ForensicFindingsPanel } from '../components/ForensicFindingsPanel'
import { RedFlagsPanel } from '../components/RedFlagsPanel'
import { ConfidencePanel } from '../components/ConfidencePanel'
import { AuditTrailPanel } from '../components/AuditTrailPanel'
import type { EstablishedModels, ForensicFinding, OverallAssessment, PillarResult } from '../../../types/efs'

describe('EFS Assessment Components', () => {
  const mockOverall: OverallAssessment = {
    score: null,
    score_status: 'CALIBRATION_PENDING',
    risk_level: null,
    confidence: 78.4,
  }

  const mockPillars: PillarResult[] = [
    {
      pillar_id: 'P1',
      pillar_name: 'Financial Statement Quality',
      pillar_score: null,
      variables_evaluated: 15,
      variables_available: 5,
      variables_missing: ['FSQ06'],
      key_positive_drivers: [],
      key_negative_drivers: ['FSQ02 — AR Growth'],
      data_quality: 'LOW',
      status: 'CALIBRATION_PENDING',
      variables: [],
    },
    {
      pillar_id: 'P2',
      pillar_name: 'Cash Flow Integrity',
      pillar_score: null,
      variables_evaluated: 15,
      variables_available: 3,
      variables_missing: [],
      key_positive_drivers: ['CFI01 — CFO Coverage'],
      key_negative_drivers: [],
      data_quality: 'MEDIUM',
      status: 'CALIBRATION_PENDING',
      variables: [],
    },
  ]

  const mockModels: EstablishedModels = {
    beneish_m_score: {
      model_id: 'MODEL01',
      model_name: 'Beneish M-Score',
      score: -1.45,
      threshold: -1.78,
      risk_signal: 'Elevated Forensic Risk',
      role: 'Supporting Evidence',
      status: 'COMPLETED',
      interpretation: 'M-Score of -1.45 indicates elevated manipulation risk.',
    },
    sloan_accrual: {
      model_id: 'MODEL02',
      model_name: 'Sloan Accrual Model',
      score: 0.09,
      threshold: 0.08,
      risk_signal: 'Elevated Accrual Risk',
      role: 'Supporting Evidence',
      status: 'COMPLETED',
      interpretation: 'Sloan Accrual Ratio of 9.00% indicates high accrual dependency.',
    },
    altman_z_score: {
      model_id: 'MODEL03',
      model_name: 'Altman Z-Score',
      score: 2.45,
      zone: 'Grey Zone',
      risk_signal: 'Moderate Distress Risk',
      role: 'Cross-Validation',
      status: 'COMPLETED',
      interpretation: 'Altman Z-Score of 2.45 places company in the Grey Zone.',
    },
    piotroski_f_score: {
      model_id: 'MODEL04',
      model_name: 'Piotroski F-Score',
      score: 7,
      max_score: 9,
      risk_signal: 'Moderate Financial Health',
      role: 'Cross-Validation',
      status: 'COMPLETED',
      interpretation: 'Piotroski F-Score of 7/9 reflects moderate financial health.',
    },
    ohlson_o_score: {
      model_id: 'MODEL05',
      model_name: 'Ohlson O-Score',
      score: 0.12,
      threshold: 0.5,
      risk_signal: 'Low Default Risk',
      role: 'Cross-Validation',
      status: 'COMPLETED',
      interpretation: 'Ohlson O-Score of 0.12 signals normal operating solvency.',
    },
  }

  const mockFindings: ForensicFinding[] = [
    {
      rule_id: 'FR-FSQ03',
      rule_name: 'DSRI — Elevated Forensic Risk',
      pillar: 'Financial Statement Quality',
      triggered: true,
      severity: 'Critical',
      trigger_condition: 'Variable > 1.40',
      evidence: 'DSRI = 1.45',
      forensic_finding: 'DSRI has entered an elevated-risk range.',
      why_it_matters: 'Deterioration in receivables relative to sales.',
      recommended_investigation: 'Perform customer aging test.',
      question_for_management: 'What explains receivables buildup?',
      evidence_state: 'Triggered',
    },
  ]

  it('1. Calibration pending state renders score as null / "—" and CALIBRATION PENDING chip', () => {
    render(
      <AssessmentStatus
        overall={mockOverall}
        variablesEvaluated={95}
        variablesAvailable={12}
        rulesEvaluated={110}
        rulesTriggered={1}
      />
    )
    expect(screen.getByText('CALIBRATION PENDING')).toBeInTheDocument()
    expect(screen.getByText('—')).toBeInTheDocument()
    expect(screen.getByText('78.4%')).toBeInTheDocument()
  })

  it('2. CalibrationNotice explains empirical calibration rationale', () => {
    render(<CalibrationNotice />)
    expect(screen.getByText("Why isn't there an EFS™ score yet?")).toBeInTheDocument()
    expect(screen.getByText(/Final weighted scoring is intentionally withheld/i)).toBeInTheDocument()
  })

  it('3. Seven Pillars render correctly with calibration-pending scores', () => {
    render(<PillarsOverview pillars={mockPillars} onSelectPillar={vi.fn()} />)
    expect(screen.getByText('Financial Statement Quality')).toBeInTheDocument()
    expect(screen.getByText('Cash Flow Integrity')).toBeInTheDocument()
    expect(screen.getAllByText('Pending Calibration').length).toBeGreaterThan(0)
  })

  it('4. Established Models render all 5 models independently with role callouts', () => {
    render(<EstablishedModelsPanel models={mockModels} />)
    expect(screen.getByText('Beneish M-Score')).toBeInTheDocument()
    expect(screen.getByText('Sloan Accrual Model')).toBeInTheDocument()
    expect(screen.getByText('Altman Z-Score')).toBeInTheDocument()
    expect(screen.getByText('Piotroski F-Score')).toBeInTheDocument()
    expect(screen.getByText('Ohlson O-Score')).toBeInTheDocument()
    expect(screen.getAllByText('Supporting Evidence').length).toBe(2)
    expect(screen.getAllByText('Cross-Validation').length).toBe(3)
  })

  it('5. Forensic Findings render triggered rules and evidence', () => {
    render(<ForensicFindingsPanel findings={mockFindings} />)
    expect(screen.getByText('DSRI — Elevated Forensic Risk')).toBeInTheDocument()
    expect(screen.getByText('DSRI has entered an elevated-risk range.')).toBeInTheDocument()
    expect(screen.getByText('"What explains receivables buildup?"')).toBeInTheDocument()
  })

  it('6. No-findings state displays appropriate message', () => {
    render(<RedFlagsPanel redFlags={[]} findings={[]} />)
    expect(
      screen.getByText(/No material forensic red flags triggered based on currently available evidence/i)
    ).toBeInTheDocument()
  })

  it('7. ConfidencePanel renders confidence percentage and quality factors', () => {
    render(
      <ConfidencePanel
        overall={mockOverall}
        limitations={['Missing 83 variables']}
        variablesAvailable={12}
        variablesEvaluated={95}
      />
    )
    expect(screen.getByText('78.4%')).toBeInTheDocument()
    expect(screen.getByText('• Missing 83 variables')).toBeInTheDocument()
  })

  it('8. AuditTrailPanel renders execution and version metadata', () => {
    const mockAudit = {
      assessment_id: 'efs_asm_test_99',
      analysis_id: 'sample_001',
      efs_version: '1.0',
      scoring_version: '1.0',
      rulebook_version: '1.0',
      engine_version: '1.0.0',
      timestamp: '2026-08-10T12:00:00Z',
      variables_evaluated: 95,
      variables_available: 12,
      rules_evaluated: 110,
      rules_triggered: 1,
      calculation_time_ms: 18.5,
    }
    render(<AuditTrailPanel auditTrail={mockAudit} />)
    expect(screen.getByText('Regulatory & Forensic Audit Trail')).toBeInTheDocument()
    expect(screen.getByText('efs_asm_test_99')).toBeInTheDocument()
  })
})
