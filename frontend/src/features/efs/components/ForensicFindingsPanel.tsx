import { useState } from 'react'
import { Box, Card, Chip, Grid, Paper, Stack, Tab, Tabs, Typography } from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import QuestionAnswerOutlinedIcon from '@mui/icons-material/QuestionAnswerOutlined'
import type { ForensicFinding, RuleSeverity } from '../../../types/efs'

interface ForensicFindingsPanelProps {
  findings: ForensicFinding[]
}

function getSeverityColor(severity: RuleSeverity): 'error' | 'warning' | 'info' | 'default' {
  switch (severity) {
    case 'Critical':
      return 'error'
    case 'High':
      return 'error'
    case 'Medium':
      return 'warning'
    case 'Low':
      return 'info'
    default:
      return 'default'
  }
}

export function ForensicFindingsPanel({ findings = [] }: ForensicFindingsPanelProps) {
  const [tabIndex, setTabIndex] = useState(0)

  const triggeredFindings = findings.filter((f) => f.triggered)

  const filterSeverity = ['ALL', 'Critical', 'High', 'Medium', 'Low', 'Context'][tabIndex]

  const filtered =
    filterSeverity === 'ALL'
      ? triggeredFindings
      : triggeredFindings.filter((f) => f.severity.toUpperCase() === filterSeverity.toUpperCase())

  return (
    <Box sx={{ mb: 4 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 700, color: '#0f172a' }}>
            Forensic Rulebook Findings ({triggeredFindings.length} Triggered / {findings.length} Evaluated)
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Deterministic evaluation of 110 forensic rules across single-variable, model, and cross-pillar conditions.
          </Typography>
        </Box>
      </Stack>

      <Paper elevation={0} sx={{ mb: 2.5, border: '1px solid #cbd5e1', borderRadius: 2 }}>
        <Tabs
          value={tabIndex}
          onChange={(_, v) => setTabIndex(v)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{ minHeight: 48, '& .MuiTab-root': { fontWeight: 700, fontSize: '0.8rem' } }}
        >
          <Tab label={`ALL TRIGGERED (${triggeredFindings.length})`} />
          <Tab label={`CRITICAL (${triggeredFindings.filter((f) => f.severity === 'Critical').length})`} />
          <Tab label={`HIGH (${triggeredFindings.filter((f) => f.severity === 'High').length})`} />
          <Tab label={`MEDIUM (${triggeredFindings.filter((f) => f.severity === 'Medium').length})`} />
          <Tab label={`LOW (${triggeredFindings.filter((f) => f.severity === 'Low').length})`} />
          <Tab label={`CONTEXT (${triggeredFindings.filter((f) => f.severity === 'Context').length})`} />
        </Tabs>
      </Paper>

      {filtered.length > 0 ? (
        <Stack spacing={2}>
          {filtered.map((f) => (
            <Card
              key={f.rule_id}
              elevation={0}
              sx={{
                p: 3,
                borderRadius: 2,
                border: '1px solid #cbd5e1',
                bgcolor: f.severity === 'Critical' ? '#fff1f2' : '#ffffff',
              }}
            >
              <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                <Box>
                  <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                    <Chip label={f.rule_id} size="small" sx={{ bgcolor: '#0f172a', color: '#ffffff', fontWeight: 800, fontFamily: 'monospace' }} />
                    <Chip label={f.severity} size="small" color={getSeverityColor(f.severity)} sx={{ fontWeight: 700 }} />
                    <Chip label={f.pillar} size="small" variant="outlined" sx={{ fontWeight: 600 }} />
                    <Chip label={f.evidence_state} size="small" color="success" variant="outlined" sx={{ fontWeight: 700 }} />
                  </Stack>

                  <Typography variant="h6" sx={{ fontWeight: 700, color: '#0f172a' }}>
                    {f.rule_name}
                  </Typography>
                </Box>
              </Stack>

              <Grid container spacing={2}>
                {/* Forensic Finding & Why It Matters */}
                <Grid size={{ xs: 12, md: 6 }}>
                  <Box sx={{ p: 2, bgcolor: '#f8fafc', borderRadius: 1.5, border: '1px solid #e2e8f0', height: '100%' }}>
                    <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 700, display: 'block' }}>
                      FORENSIC FINDING STATEMENT
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 700, color: '#0f172a', mt: 0.5, mb: 1.5 }}>
                      {f.forensic_finding}
                    </Typography>

                    <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 700, display: 'block' }}>
                      WHY IT MATTERS
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#334155', mt: 0.5 }}>
                      {f.why_it_matters}
                    </Typography>
                  </Box>
                </Grid>

                {/* Evidence & Trigger Condition */}
                <Grid size={{ xs: 12, md: 6 }}>
                  <Box sx={{ p: 2, bgcolor: '#f8fafc', borderRadius: 1.5, border: '1px solid #e2e8f0', height: '100%' }}>
                    <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 700, display: 'block' }}>
                      EVIDENCE & TRIGGER CONDITION
                    </Typography>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 700, color: '#b91c1c', mt: 0.5, mb: 1.5 }}>
                      {f.evidence}
                    </Typography>

                    <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 700, display: 'block' }}>
                      CONDITION RULEBOOK SPECIFICATION
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#475569', display: 'block', mt: 0.5 }}>
                      {f.trigger_condition}
                    </Typography>
                  </Box>
                </Grid>

                {/* Recommended Investigation & Management Question */}
                <Grid size={{ xs: 12 }}>
                  <Box sx={{ p: 2, bgcolor: '#eff6ff', borderRadius: 1.5, border: '1px solid #bfdbfe' }}>
                    <Grid container spacing={2}>
                      <Grid size={{ xs: 12, md: 6 }}>
                        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.5 }}>
                          <SearchIcon sx={{ color: '#1d4ed8', fontSize: 18 }} />
                          <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#1e40af' }}>
                            Recommended Audit Procedure
                          </Typography>
                        </Stack>
                        <Typography variant="body2" sx={{ color: '#1e3a8a' }}>
                          {f.recommended_investigation}
                        </Typography>
                      </Grid>

                      <Grid size={{ xs: 12, md: 6 }}>
                        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.5 }}>
                          <QuestionAnswerOutlinedIcon sx={{ color: '#1d4ed8', fontSize: 18 }} />
                          <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#1e40af' }}>
                            Question for Management
                          </Typography>
                        </Stack>
                        <Typography variant="body2" sx={{ color: '#1e3a8a', fontWeight: 600 }}>
                          "{f.question_for_management}"
                        </Typography>
                      </Grid>
                    </Grid>
                  </Box>
                </Grid>
              </Grid>
            </Card>
          ))}
        </Stack>
      ) : (
        <Paper elevation={0} sx={{ p: 4, textAlign: 'center', bgcolor: '#ffffff', border: '1px solid #cbd5e1', borderRadius: 2 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#475569' }}>
            No forensic findings triggered for severity: {filterSeverity}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            No material forensic rules were triggered based on the currently available evidence.
          </Typography>
        </Paper>
      )}
    </Box>
  )
}
