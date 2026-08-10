import { Box, Card, Chip, Grid, Paper, Stack, Typography } from '@mui/material'
import type { EstablishedModel, EstablishedModels } from '../../../types/efs'

interface EstablishedModelsPanelProps {
  models: EstablishedModels
}

function getRiskSignalChipColor(signal: string): 'error' | 'warning' | 'success' | 'info' | 'default' {
  if (signal.includes('Elevated') || signal.includes('Distress') || signal.includes('Weak')) return 'error'
  if (signal.includes('Moderate') || signal.includes('Grey')) return 'warning'
  if (signal.includes('Low') || signal.includes('Strong')) return 'success'
  return 'default'
}

export function EstablishedModelsPanel({ models }: EstablishedModelsPanelProps) {
  if (!models) return null

  const modelList: EstablishedModel[] = [
    models.beneish_m_score,
    models.sloan_accrual,
    models.altman_z_score,
    models.piotroski_f_score,
    models.ohlson_o_score,
  ].filter(Boolean)

  return (
    <Box sx={{ mb: 4 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 700, color: '#0f172a' }}>
            Established Financial Models
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Five classic forensic, accounting, and insolvency models evaluated independently.
          </Typography>
        </Box>
      </Stack>

      <Paper
        elevation={0}
        sx={{
          p: 2,
          mb: 2.5,
          borderRadius: 2,
          bgcolor: '#f8fafc',
          border: '1px solid #e2e8f0',
        }}
      >
        <Typography variant="caption" sx={{ color: '#475569', fontWeight: 600, display: 'block' }}>
          METHODOLOGY RULE: SEPARATE VISIBILITY & NO COMPOSITE SCORING
        </Typography>
        <Typography variant="body2" sx={{ color: '#64748b', mt: 0.5 }}>
          Per EFS™ methodology, these established models are evaluated independently and kept separately visible. They are NOT combined into a composite score to avoid double-counting or treating them as fraud declarations.
        </Typography>
      </Paper>

      <Grid container spacing={2}>
        {modelList.map((m, idx) => (
          <Grid size={{ xs: 12, sm: 6, lg: 4 }} key={m?.model_id || idx}>
            <Card
              elevation={0}
              sx={{
                p: 2.5,
                borderRadius: 2,
                border: '1px solid #cbd5e1',
                bgcolor: '#ffffff',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <Box>
                <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 1.5 }}>
                  <Chip
                    label={m.role}
                    size="small"
                    color={m.role === 'Supporting Evidence' ? 'primary' : 'secondary'}
                    variant="outlined"
                    sx={{ fontWeight: 700, fontSize: '0.7rem' }}
                  />
                  <Chip
                    label={m.status}
                    size="small"
                    color={m.status === 'COMPLETED' ? 'success' : 'default'}
                    sx={{ fontWeight: 700, fontSize: '0.7rem' }}
                  />
                </Stack>

                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#0f172a' }}>
                  {m.model_name}
                </Typography>
                <Typography variant="caption" sx={{ color: '#64748b', display: 'block', mb: 1.5 }}>
                  {m.specification || m.model_id}
                </Typography>

                <Box sx={{ p: 1.5, bgcolor: '#f8fafc', borderRadius: 1.5, border: '1px solid #e2e8f0', mb: 2 }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 600 }}>
                      RESULT / SCORE
                    </Typography>
                    <Typography variant="h6" sx={{ fontWeight: 800, color: '#0f172a' }}>
                      {m.score !== null ? m.score : '—'}
                    </Typography>
                  </Stack>

                  <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 1 }}>
                    <Chip
                      label={m.risk_signal || m.zone || 'No Signal'}
                      size="small"
                      color={getRiskSignalChipColor(m.risk_signal)}
                      sx={{ fontWeight: 700, fontSize: '0.7rem' }}
                    />
                    {m.threshold !== undefined && (
                      <Typography variant="caption" color="text.secondary">
                        (Threshold: {m.threshold})
                      </Typography>
                    )}
                  </Stack>
                </Box>
              </Box>

              <Typography variant="body2" sx={{ color: '#475569', fontSize: '0.8125rem', lineHeight: 1.4 }}>
                "{m.interpretation}"
              </Typography>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}
