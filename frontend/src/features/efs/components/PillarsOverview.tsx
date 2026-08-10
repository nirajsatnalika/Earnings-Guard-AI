import { Box, Button, Card, Chip, Grid, LinearProgress, Stack, Typography } from '@mui/material'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import AnalyticsOutlinedIcon from '@mui/icons-material/AnalyticsOutlined'
import type { DataQualityLevel, PillarResult } from '../../../types/efs'

interface PillarsOverviewProps {
  pillars: PillarResult[]
  onSelectPillar: (pillar: PillarResult) => void
}

function getDataQualityColor(level: DataQualityLevel): 'success' | 'warning' | 'error' | 'default' {
  switch (level) {
    case 'HIGH':
      return 'success'
    case 'MEDIUM':
      return 'warning'
    case 'LOW':
    case 'INSUFFICIENT':
      return 'error'
    default:
      return 'default'
  }
}

export function PillarsOverview({ pillars = [], onSelectPillar }: PillarsOverviewProps) {
  return (
    <Box sx={{ mb: 4 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 700, color: '#0f172a' }}>
            Seven Assessment Pillars
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Comprehensive forensic evaluation across 95 variables and 7 methodology pillars.
          </Typography>
        </Box>
      </Stack>

      <Grid container spacing={2}>
        {pillars.map((p, idx) => {
          const availPct = p.variables_evaluated > 0 ? (p.variables_available / p.variables_evaluated) * 100 : 0

          return (
            <Grid size={{ xs: 12, sm: 6, lg: 4 }} key={p.pillar_id || idx}>
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
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    borderColor: '#635bff',
                    boxShadow: '0 4px 12px rgba(99, 91, 255, 0.08)',
                  },
                }}
              >
                <Box>
                  <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 1.5 }}>
                    <Chip
                      label={p.pillar_id}
                      size="small"
                      sx={{ bgcolor: '#f1f5f9', color: '#475569', fontWeight: 800, fontFamily: 'monospace' }}
                    />
                    <Chip
                      label={`Data Quality: ${p.data_quality}`}
                      size="small"
                      color={getDataQualityColor(p.data_quality)}
                      variant="outlined"
                      sx={{ fontWeight: 700, fontSize: '0.7rem' }}
                    />
                  </Stack>

                  <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#0f172a', mb: 1 }}>
                    {p.pillar_name}
                  </Typography>

                  <Box sx={{ p: 1.5, bgcolor: '#f8fafc', borderRadius: 1.5, border: '1px solid #e2e8f0', mb: 2 }}>
                    <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 600, display: 'block' }}>
                      PILLAR SCORE
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 700, color: '#b45309', mt: 0.2 }}>
                      Pending Calibration
                    </Typography>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Stack direction="row" justifyContent="space-between" sx={{ mb: 0.5 }}>
                      <Typography variant="caption" color="text.secondary">
                        Variables Available
                      </Typography>
                      <Typography variant="caption" sx={{ fontWeight: 700, color: '#334155' }}>
                        {p.variables_available} / {p.variables_evaluated} ({availPct.toFixed(0)}%)
                      </Typography>
                    </Stack>
                    <LinearProgress
                      variant="determinate"
                      value={availPct}
                      sx={{ height: 6, borderRadius: 3, bgcolor: '#e2e8f0', '& .MuiLinearProgress-bar': { bgcolor: '#475569' } }}
                    />
                  </Box>

                  <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                    {p.key_negative_drivers.length > 0 && (
                      <Chip
                        label={`${p.key_negative_drivers.length} Negative Drivers`}
                        size="small"
                        sx={{ bgcolor: '#fef2f2', color: '#991b1b', fontWeight: 600, fontSize: '0.7rem' }}
                      />
                    )}
                    {p.key_positive_drivers.length > 0 && (
                      <Chip
                        label={`${p.key_positive_drivers.length} Positive Drivers`}
                        size="small"
                        sx={{ bgcolor: '#f0fdf4', color: '#166534', fontWeight: 600, fontSize: '0.7rem' }}
                      />
                    )}
                  </Stack>
                </Box>

                <Button
                  variant="outlined"
                  size="small"
                  fullWidth
                  endIcon={<ChevronRightIcon />}
                  startIcon={<AnalyticsOutlinedIcon />}
                  onClick={() => onSelectPillar(p)}
                  sx={{ mt: 1, borderColor: '#cbd5e1', color: '#334155', fontWeight: 600 }}
                >
                  View Variable Evidence ({p.variables?.length || 0})
                </Button>
              </Card>
            </Grid>
          )
        })}
      </Grid>
    </Box>
  )
}
