import { Box, Card, Chip, Paper, Stack, Typography } from '@mui/material'
import WarningAmberIcon from '@mui/icons-material/WarningAmber'
import type { ForensicFinding } from '../../../types/efs'

interface RedFlagsPanelProps {
  redFlags: string[]
  findings: ForensicFinding[]
  onSelectFinding?: (finding: ForensicFinding) => void
}

export function RedFlagsPanel({ redFlags = [], findings = [], onSelectFinding }: RedFlagsPanelProps) {
  const triggeredFindings = findings.filter((f) => f.triggered)

  if (redFlags.length === 0 && triggeredFindings.length === 0) {
    return (
      <Paper elevation={0} sx={{ p: 2.5, mb: 3, borderRadius: 2, bgcolor: '#f0fdf4', border: '1px solid #bbf7d0' }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#166534' }}>
          Key Forensic Red Flags
        </Typography>
        <Typography variant="body2" sx={{ color: '#15803d', mt: 0.5 }}>
          No material forensic red flags triggered based on currently available evidence.
        </Typography>
      </Paper>
    )
  }

  return (
    <Box sx={{ mb: 4 }}>
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
        <WarningAmberIcon sx={{ color: '#dc2626' }} />
        <Typography variant="h6" sx={{ fontWeight: 700, color: '#0f172a' }}>
          Key Forensic Red Flags ({triggeredFindings.length > 0 ? triggeredFindings.length : redFlags.length})
        </Typography>
      </Stack>

      <Stack spacing={1.5}>
        {triggeredFindings.length > 0
          ? triggeredFindings.map((f) => (
              <Card
                key={f.rule_id}
                elevation={0}
                onClick={() => onSelectFinding?.(f)}
                sx={{
                  p: 2,
                  borderRadius: 2,
                  bgcolor: '#fff1f2',
                  border: '1px solid #fecdd3',
                  cursor: onSelectFinding ? 'pointer' : 'default',
                  transition: 'all 0.15s ease',
                  '&:hover': {
                    bgcolor: '#ffe4e6',
                  },
                }}
              >
                <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                  <Box>
                    <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.5 }}>
                      <Chip label={f.rule_id} size="small" sx={{ bgcolor: '#be123c', color: '#ffffff', fontWeight: 800, fontSize: '0.7rem' }} />
                      <Chip label={f.severity} size="small" color={f.severity === 'Critical' ? 'error' : 'warning'} sx={{ fontWeight: 700 }} />
                      <Chip label={f.pillar} size="small" variant="outlined" sx={{ fontWeight: 600, fontSize: '0.7rem' }} />
                    </Stack>
                    <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#881337' }}>
                      {f.rule_name}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#9f1239', mt: 0.5 }}>
                      {f.forensic_finding}
                    </Typography>
                  </Box>

                  <Chip label="View Evidence" size="small" variant="outlined" sx={{ color: '#be123c', borderColor: '#f43f5e' }} />
                </Stack>
              </Card>
            ))
          : redFlags.map((flag, idx) => (
              <Card key={idx} elevation={0} sx={{ p: 2, borderRadius: 2, bgcolor: '#fff1f2', border: '1px solid #fecdd3' }}>
                <Typography variant="body2" sx={{ color: '#9f1239', fontWeight: 600 }}>
                  • {flag}
                </Typography>
              </Card>
            ))}
      </Stack>
    </Box>
  )
}
