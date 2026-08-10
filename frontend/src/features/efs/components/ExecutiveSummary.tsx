import { Box, Card, Grid, Stack, Typography } from '@mui/material'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'
import WarningOutlinedIcon from '@mui/icons-material/WarningOutlined'
import ReportProblemOutlinedIcon from '@mui/icons-material/ReportProblemOutlined'
import type { ForensicFinding, PillarResult } from '../../../types/efs'

interface ExecutiveSummaryProps {
  pillars: PillarResult[]
  findings: ForensicFinding[]
  limitations: string[]
}

export function ExecutiveSummary({ pillars = [], findings = [], limitations = [] }: ExecutiveSummaryProps) {
  // Aggregate key positive and negative drivers deterministically
  const positiveDrivers: string[] = []
  const negativeDrivers: string[] = []

  pillars.forEach((p) => {
    p.key_positive_drivers.forEach((d) => positiveDrivers.push(`${p.pillar_name}: ${d}`))
    p.key_negative_drivers.forEach((d) => negativeDrivers.push(`${p.pillar_name}: ${d}`))
  })

  const criticalFindings = findings.filter((f) => f.triggered && (f.severity === 'Critical' || f.severity === 'High'))

  return (
    <Card elevation={0} sx={{ p: 3, mb: 3, borderRadius: 2, border: '1px solid #cbd5e1' }}>
      <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, color: '#0f172a' }}>
        Executive Forensic Summary
      </Typography>

      <Grid container spacing={2}>
        {/* Key Positive Signals */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Box sx={{ p: 2, borderRadius: 2, bgcolor: '#f0fdf4', border: '1px solid #bbf7d0', height: '100%' }}>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
              <CheckCircleOutlineIcon sx={{ color: '#16a34a' }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#14532d' }}>
                Key Positive Signals ({positiveDrivers.length})
              </Typography>
            </Stack>
            {positiveDrivers.length > 0 ? (
              <Stack spacing={0.8}>
                {positiveDrivers.map((item, idx) => (
                  <Typography key={idx} variant="body2" sx={{ color: '#166534', fontWeight: 500 }}>
                    • {item}
                  </Typography>
                ))}
              </Stack>
            ) : (
              <Typography variant="body2" sx={{ color: '#64748b' }}>
                No significant positive drivers flagged based on available inputs.
              </Typography>
            )}
          </Box>
        </Grid>

        {/* Key Negative Signals */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Box sx={{ p: 2, borderRadius: 2, bgcolor: '#fef2f2', border: '1px solid #fecaca', height: '100%' }}>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
              <ErrorOutlineIcon sx={{ color: '#dc2626' }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#7f1d1d' }}>
                Key Negative Signals ({negativeDrivers.length})
              </Typography>
            </Stack>
            {negativeDrivers.length > 0 ? (
              <Stack spacing={0.8}>
                {negativeDrivers.map((item, idx) => (
                  <Typography key={idx} variant="body2" sx={{ color: '#991b1b', fontWeight: 500 }}>
                    • {item}
                  </Typography>
                ))}
              </Stack>
            ) : (
              <Typography variant="body2" sx={{ color: '#64748b' }}>
                No key negative drivers flagged.
              </Typography>
            )}
          </Box>
        </Grid>

        {/* Critical Findings */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Box sx={{ p: 2, borderRadius: 2, bgcolor: '#fff7ed', border: '1px solid #ffedd5', height: '100%' }}>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
              <WarningOutlinedIcon sx={{ color: '#ea580c' }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#7c2d12' }}>
                Critical & High Severity Findings ({criticalFindings.length})
              </Typography>
            </Stack>
            {criticalFindings.length > 0 ? (
              <Stack spacing={1}>
                {criticalFindings.map((f) => (
                  <Box key={f.rule_id}>
                    <Typography variant="body2" sx={{ fontWeight: 700, color: '#9a3412' }}>
                      [{f.rule_id}] {f.rule_name}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#c2410c' }}>
                      {f.forensic_finding}
                    </Typography>
                  </Box>
                ))}
              </Stack>
            ) : (
              <Typography variant="body2" sx={{ color: '#64748b' }}>
                No material forensic rules were triggered based on the available evidence.
              </Typography>
            )}
          </Box>
        </Grid>

        {/* Data Limitations */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Box sx={{ p: 2, borderRadius: 2, bgcolor: '#f8fafc', border: '1px solid #e2e8f0', height: '100%' }}>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
              <ReportProblemOutlinedIcon sx={{ color: '#64748b' }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#334155' }}>
                Data Quality & Coverage Limitations ({limitations.length})
              </Typography>
            </Stack>
            {limitations.length > 0 ? (
              <Stack spacing={0.8}>
                {limitations.map((lim, idx) => (
                  <Typography key={idx} variant="body2" sx={{ color: '#475569' }}>
                    • {lim}
                  </Typography>
                ))}
              </Stack>
            ) : (
              <Typography variant="body2" sx={{ color: '#64748b' }}>
                No data coverage limitations reported.
              </Typography>
            )}
          </Box>
        </Grid>
      </Grid>
    </Card>
  )
}
