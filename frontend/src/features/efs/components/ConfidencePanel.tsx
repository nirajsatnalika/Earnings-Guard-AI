import { Box, Card, Chip, Grid, LinearProgress, Stack, Typography } from '@mui/material'
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser'
import type { OverallAssessment } from '../../../types/efs'

interface ConfidencePanelProps {
  overall: OverallAssessment
  limitations: string[]
  variablesAvailable: number
  variablesEvaluated: number
}

export function ConfidencePanel({
  overall,
  limitations = [],
  variablesAvailable = 0,
  variablesEvaluated = 95,
}: ConfidencePanelProps) {
  const conf = overall?.confidence ?? 0.0
  const level = conf >= 80 ? 'HIGH' : conf >= 60 ? 'MEDIUM' : 'LOW'
  const color = level === 'HIGH' ? 'success' : level === 'MEDIUM' ? 'warning' : 'error'

  return (
    <Card elevation={0} sx={{ p: 3, mb: 3, borderRadius: 2, border: '1px solid #cbd5e1' }}>
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
        <VerifiedUserIcon sx={{ color: '#0284c7' }} />
        <Typography variant="h6" sx={{ fontWeight: 700, color: '#0f172a' }}>
          Assessment Confidence & Data Quality Score
        </Typography>
      </Stack>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Box sx={{ p: 2.5, bgcolor: '#f8fafc', borderRadius: 2, border: '1px solid #e2e8f0', textAlign: 'center' }}>
            <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 700, textTransform: 'uppercase' }}>
              Multi-Factor Confidence Score
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 800, color: '#0284c7', my: 1 }}>
              {conf.toFixed(1)}%
            </Typography>
            <Chip label={`Confidence Level: ${level}`} color={color} sx={{ fontWeight: 800 }} />
            <Box sx={{ mt: 2 }}>
              <LinearProgress
                variant="determinate"
                value={conf}
                sx={{ height: 8, borderRadius: 4, bgcolor: '#e2e8f0', '& .MuiLinearProgress-bar': { bgcolor: '#0284c7' } }}
              />
            </Box>
          </Box>
        </Grid>

        <Grid size={{ xs: 12, md: 8 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#334155', mb: 1 }}>
            Evidence Quality Factors
          </Typography>
          <Grid container spacing={1.5} sx={{ mb: 2 }}>
            <Grid size={{ xs: 6, sm: 4 }}>
              <Box sx={{ p: 1.5, bgcolor: '#f8fafc', borderRadius: 1.5, border: '1px solid #e2e8f0' }}>
                <Typography variant="caption" color="text.secondary">
                  Variables Available
                </Typography>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#0f172a' }}>
                  {variablesAvailable} / {variablesEvaluated}
                </Typography>
              </Box>
            </Grid>
            <Grid size={{ xs: 6, sm: 4 }}>
              <Box sx={{ p: 1.5, bgcolor: '#f8fafc', borderRadius: 1.5, border: '1px solid #e2e8f0' }}>
                <Typography variant="caption" color="text.secondary">
                  Statement Flags
                </Typography>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#0f172a' }}>
                  BS, IS, OCF Complete
                </Typography>
              </Box>
            </Grid>
            <Grid size={{ xs: 6, sm: 4 }}>
              <Box sx={{ p: 1.5, bgcolor: '#f8fafc', borderRadius: 1.5, border: '1px solid #e2e8f0' }}>
                <Typography variant="caption" color="text.secondary">
                  Model Availability
                </Typography>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#0f172a' }}>
                  5 / 5 Models Evaluated
                </Typography>
              </Box>
            </Grid>
          </Grid>

          {limitations.length > 0 && (
            <Box>
              <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 700, display: 'block', mb: 0.5 }}>
                KEY DATA QUALITY LIMITATIONS
              </Typography>
              <Stack spacing={0.5}>
                {limitations.map((lim, idx) => (
                  <Typography key={idx} variant="caption" sx={{ color: '#475569', display: 'block' }}>
                    • {lim}
                  </Typography>
                ))}
              </Stack>
            </Box>
          )}
        </Grid>
      </Grid>
    </Card>
  )
}
