import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { AINarrativePanel } from '../components/AINarrativePanel'
import type { EFSNarrativeResponse } from '../../../types/efs'

const mockNarrative: EFSNarrativeResponse = {
  narrative_version: '1.0',
  analysis_id: 'sample_analysis_001',
  assessment_id: 'efs_asm_test_001',
  generated_at: '2026-08-10T12:00:00Z',
  executive_summary: 'The assessment identified elevated forensic risk in receivables and cash conversion.',
  overall_interpretation: 'Deterministic EFS score is CALIBRATION PENDING. Underlying evidence indicates specific findings requiring corroboration.',
  key_findings: [
    {
      rule_id: 'FR-001',
      title: 'DSRI / Revenue Deterioration',
      what_observed: 'Receivables growth exceeded revenue growth by 25%.',
      why_it_matters: 'Indicates potential uncollected reported revenue.',
      supporting_evidence: 'Rule FR-001 (High severity)',
      legitimate_explanations: ['Credit term changes'],
      investigation_next_steps: 'Inspect customer ledger ageing.',
      evidence_refs: ['FSQ02', 'FR-001'],
    },
  ],
  pillar_narratives: [
    {
      pillar_id: 'P1',
      pillar_name: 'Financial Statement Quality',
      summary: 'Evaluated 12 variables with medium data quality.',
      positive_signals: [],
      adverse_signals: ['Receivables growth anomaly'],
      missing_evidence: [],
      investigation_areas: ['Verify sales cut-off'],
    },
  ],
  model_interpretations: [],
  cross_signal_analysis: [],
  investigation_priorities: [],
  management_questions_context: [],
  data_limitations: ['Historical disclosures missing'],
  methodology_note: 'EFS is deterministic.',
  disclaimer: 'AI-GENERATED FORENSIC INTERPRETATION. The deterministic EFS™ engine remains the forensic assessment authority.',
  provider_info: {
    provider: 'deterministic-fallback',
    model: 'rule-based-synthesizer',
    fallback_used: true,
  },
}

describe('AINarrativePanel Component', () => {
  it('renders AI FORENSIC INTERPRETATION header and badge', () => {
    render(<AINarrativePanel analysisId="sample_analysis_001" initialNarrative={mockNarrative} />)
    expect(screen.getByText(/AI FORENSIC INTERPRETATION/i)).toBeInTheDocument()
    expect(screen.getByText(/AI-GENERATED INTERPRETATION/i)).toBeInTheDocument()
  })

  it('renders executive summary and overall calibration-pending interpretation', () => {
    render(<AINarrativePanel analysisId="sample_analysis_001" initialNarrative={mockNarrative} />)
    expect(screen.getByText(/elevated forensic risk in receivables/i)).toBeInTheDocument()
    expect(screen.getByText(/CALIBRATION PENDING/i)).toBeInTheDocument()
  })

  it('displays key finding with evidence reference tag', () => {
    render(<AINarrativePanel analysisId="sample_analysis_001" initialNarrative={mockNarrative} />)
    expect(screen.getByText(/DSRI \/ Revenue Deterioration/i)).toBeInTheDocument()
    expect(screen.getAllByText('FR-001').length).toBeGreaterThan(0)
  })
})
