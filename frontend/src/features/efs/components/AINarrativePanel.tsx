import { useState, useEffect } from 'react'
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Box,
  Chip,
  CircularProgress,
  Divider,
  Paper,
  Stack,
  Typography,
} from '@mui/material'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined'
import WarningAmberIcon from '@mui/icons-material/WarningAmber'

import { EFSService } from '../../../services/api/efsService'
import type { EFSNarrativeResponse } from '../../../types/efs'

interface AINarrativePanelProps {
  analysisId: string
  initialNarrative?: EFSNarrativeResponse | null
}

export function AINarrativePanel({ analysisId, initialNarrative = null }: AINarrativePanelProps) {
  const [narrative, setNarrative] = useState<EFSNarrativeResponse | null>(initialNarrative)
  const [loading, setLoading] = useState<boolean>(!initialNarrative)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (initialNarrative) {
      setNarrative(initialNarrative)
      setLoading(false)
      return
    }

    let isMounted = true
    async function loadNarrative() {
      setLoading(true)
      setError(null)
      try {
        const data = await EFSService.getNarrative(analysisId)
        if (isMounted) setNarrative(data)
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to generate AI narrative.')
        }
      } finally {
        if (isMounted) setLoading(false)
      }
    }

    loadNarrative()
    return () => {
      isMounted = false
    }
  }, [analysisId, initialNarrative])

  if (loading) {
    return (
      <Paper elevation={0} sx={{ p: 4, mb: 3, border: '1px solid #cbd5e1', borderRadius: 2, textAlign: 'center' }}>
        <CircularProgress size={32} sx={{ color: '#4f46e5', mb: 1.5 }} />
        <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#1e1b4b' }}>
          Generating AI Forensic Interpretation...
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Synthesizing deterministic backend evidence into structured explanations.
        </Typography>
      </Paper>
    )
  }

  if (error) {
    return (
      <Paper elevation={0} sx={{ p: 3, mb: 3, border: '1px solid #fecaca', borderRadius: 2, bgcolor: '#fef2f2' }}>
        <Alert severity="warning" icon={<WarningAmberIcon />}>
          <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
            AI Narrative Temporarily Unavailable
          </Typography>
          <Typography variant="body2">{error}</Typography>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
            Deterministic EFS assessment remains 100% available and authoritative.
          </Typography>
        </Alert>
      </Paper>
    )
  }

  if (!narrative) return null

  return (
    <Paper
      elevation={0}
      sx={{
        p: { xs: 2.5, md: 3.5 },
        mb: 4,
        border: '2px solid #6366f1',
        borderRadius: 2.5,
        background: 'linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)',
      }}
    >
      {/* Header Badge & Title */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Stack direction="row" spacing={1.5} alignItems="center">
          <AutoAwesomeIcon sx={{ color: '#4f46e5', fontSize: 28 }} />
          <Typography variant="h6" sx={{ fontWeight: 800, color: '#1e1b4b' }}>
            AI FORENSIC INTERPRETATION
          </Typography>
        </Stack>
        <Chip
          label="AI-GENERATED INTERPRETATION"
          size="small"
          sx={{
            bgcolor: '#e0e7ff',
            color: '#3730a3',
            fontWeight: 700,
            fontSize: '0.75rem',
            border: '1px solid #c7d2fe',
          }}
        />
      </Box>

      {/* Methodology & Disclaimer Notice */}
      <Alert severity="info" icon={<InfoOutlinedIcon sx={{ color: '#4f46e5' }} />} sx={{ mb: 3, bgcolor: '#eeeffe', border: '1px solid #c7d2fe' }}>
        <Typography variant="caption" sx={{ color: '#312e81', display: 'block', lineHeight: 1.5 }}>
          <strong>Forensic Scope:</strong> {narrative.disclaimer}
        </Typography>
      </Alert>

      {/* 1. Executive Summary */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#4338ca', textTransform: 'uppercase', letterSpacing: 0.5, mb: 1 }}>
          Executive Forensic Summary
        </Typography>
        <Typography variant="body1" sx={{ color: '#1e293b', lineHeight: 1.7, bgcolor: '#ffffff', p: 2, borderRadius: 1.5, border: '1px solid #e2e8f0' }}>
          {narrative.executive_summary}
        </Typography>
      </Box>

      {/* 2. Overall Interpretation & Calibration Note */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#4338ca', textTransform: 'uppercase', letterSpacing: 0.5, mb: 1 }}>
          Overall Assessment Interpretation
        </Typography>
        <Typography variant="body2" sx={{ color: '#334155', lineHeight: 1.6, bgcolor: '#ffffff', p: 2, borderRadius: 1.5, border: '1px solid #e2e8f0' }}>
          {narrative.overall_interpretation}
        </Typography>
      </Box>

      {/* 3. Key Findings with Traceability */}
      {narrative.key_findings.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#4338ca', textTransform: 'uppercase', letterSpacing: 0.5, mb: 1.5 }}>
            Key Forensic Findings
          </Typography>
          <Stack spacing={1.5}>
            {narrative.key_findings.map((finding, idx) => (
              <Accordion key={idx} elevation={0} sx={{ border: '1px solid #cbd5e1', '&:before': { display: 'none' } }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, width: '100%' }}>
                    {finding.rule_id && (
                      <Chip label={finding.rule_id} size="small" sx={{ bgcolor: '#f1f5f9', fontWeight: 700, fontSize: '0.75rem' }} />
                    )}
                    <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#0f172a' }}>
                      {finding.title}
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ bgcolor: '#f8fafc', borderTop: '1px solid #e2e8f0', p: 2.5 }}>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Observation:</strong> {finding.what_observed}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Why It Matters:</strong> {finding.why_it_matters}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Supporting Evidence:</strong> {finding.supporting_evidence}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    <strong>Recommended Next Steps:</strong> {finding.investigation_next_steps}
                  </Typography>
                  {finding.evidence_refs.length > 0 && (
                    <Stack direction="row" spacing={1} sx={{ mt: 1.5 }}>
                      <Typography variant="caption" sx={{ fontWeight: 700, color: '#64748b' }}>Cited Evidence:</Typography>
                      {finding.evidence_refs.map((ref, rIdx) => (
                        <Chip key={rIdx} label={ref} size="small" variant="outlined" sx={{ height: 20, fontSize: '0.7rem' }} />
                      ))}
                    </Stack>
                  )}
                </AccordionDetails>
              </Accordion>
            ))}
          </Stack>
        </Box>
      )}

      {/* 4. Cross-Signal Analysis */}
      {narrative.cross_signal_analysis.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#4338ca', textTransform: 'uppercase', letterSpacing: 0.5, mb: 1.5 }}>
            Multi-Signal Convergence Analysis
          </Typography>
          {narrative.cross_signal_analysis.map((item, idx) => (
            <Paper key={idx} elevation={0} sx={{ p: 2, mb: 1.5, bgcolor: '#ffffff', border: '1px solid #cbd5e1' }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#1e3a8a', mb: 0.5 }}>
                {item.theme}
              </Typography>
              <Typography variant="body2" sx={{ color: '#334155', mb: 1, lineHeight: 1.6 }}>
                {item.explanation}
              </Typography>
              {item.cited_rules.length > 0 && (
                <Stack direction="row" spacing={1} alignItems="center">
                  <Typography variant="caption" sx={{ fontWeight: 700, color: '#64748b' }}>Converging Rules:</Typography>
                  {item.cited_rules.map((r, rIdx) => (
                    <Chip key={rIdx} label={r} size="small" color="primary" variant="outlined" sx={{ height: 20, fontSize: '0.7rem' }} />
                  ))}
                </Stack>
              )}
            </Paper>
          ))}
        </Box>
      )}

      {/* 5. Pillar Narratives */}
      {narrative.pillar_narratives.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#4338ca', textTransform: 'uppercase', letterSpacing: 0.5, mb: 1.5 }}>
            Seven Pillars Narrative Synthesis
          </Typography>
          <Stack spacing={1.5}>
            {narrative.pillar_narratives.map((p, idx) => (
              <Accordion key={idx} elevation={0} sx={{ border: '1px solid #e2e8f0', '&:before': { display: 'none' } }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#1e293b' }}>
                    {p.pillar_name}
                  </Typography>
                </AccordionSummary>
                <AccordionDetails sx={{ bgcolor: '#ffffff', borderTop: '1px solid #f1f5f9', p: 2 }}>
                  <Typography variant="body2" sx={{ color: '#334155', mb: 1.5 }}>
                    {p.summary}
                  </Typography>
                  {p.adverse_signals.length > 0 && (
                    <Typography variant="caption" sx={{ display: 'block', color: '#991b1b', mb: 0.5 }}>
                      <strong>Adverse Signals:</strong> {p.adverse_signals.join('; ')}
                    </Typography>
                  )}
                  {p.positive_signals.length > 0 && (
                    <Typography variant="caption" sx={{ display: 'block', color: '#166534', mb: 0.5 }}>
                      <strong>Positive Signals:</strong> {p.positive_signals.join('; ')}
                    </Typography>
                  )}
                </AccordionDetails>
              </Accordion>
            ))}
          </Stack>
        </Box>
      )}

      <Divider sx={{ my: 2 }} />

      {/* Footer Provider Info */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          Provider: {narrative.provider_info?.provider || 'deterministic'} ({narrative.provider_info?.model || 'synthesizer'})
          {narrative.provider_info?.fallback_used && ' [Fallback Mode Active]'}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Generated: {narrative.generated_at ? narrative.generated_at.substring(0, 10) : ''}
        </Typography>
      </Box>
    </Paper>
  )
}
