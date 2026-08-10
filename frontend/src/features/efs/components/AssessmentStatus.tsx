import { Box, Card, Chip, Grid, Stack, Typography } from '@mui/material'
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty'
import ShieldOutlinedIcon from '@mui/icons-material/ShieldOutlined'
import RulesIcon from '@mui/icons-material/RuleFolderOutlined'
import VariablesIcon from '@mui/icons-material/DataObjectOutlined'
import WarningAmberIcon from '@mui/icons-material/WarningAmber'
import type { OverallAssessment } from '../../../types/efs'

interface AssessmentStatusProps {
  overall: OverallAssessment
  variablesEvaluated: number
  variablesAvailable: number
  rulesEvaluated: number
  rulesTriggered: number
}

export function AssessmentStatus({
  overall,
  variablesEvaluated = 95,
  variablesAvailable = 0,
  rulesEvaluated = 110,
  rulesTriggered = 0,
}: AssessmentStatusProps) {
  return (
    <Card
      elevation={0}
      sx={{
        p: 3,
        mb: 3,
        borderRadius: 2,
        border: '1px solid #cbd5e1',
        bgcolor: '#ffffff',
      }}
    >
      <Grid container spacing={3} alignItems="center">
        {/* Main EFS Score Box */}
        <Grid size={{ xs: 12, md: 5 }}>
          <Stack direction="row" spacing={2.5} alignItems="center">
            <Box
              sx={{
                width: 100,
                height: 100,
                borderRadius: 3,
                bgcolor: '#f1f5f9',
                border: '2px dashed #94a3b8',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Typography variant="h3" sx={{ fontWeight: 800, color: '#475569' }}>
                —
              </Typography>
              <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 700, fontSize: '0.65rem' }}>
                SCORE
              </Typography>
            </Box>

            <Box>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                <Chip
                  icon={<HourglassEmptyIcon sx={{ fontSize: '16px !important', color: '#d97706 !important' }} />}
                  label="CALIBRATION PENDING"
                  sx={{
                    bgcolor: '#fef3c7',
                    color: '#b45309',
                    fontWeight: 800,
                    fontSize: '0.75rem',
                    letterSpacing: '0.04em',
                    border: '1px solid #fde68a',
                  }}
                />
              </Stack>
              <Typography variant="h6" sx={{ fontWeight: 700, color: '#0f172a' }}>
                EFS™ Forensic Score
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, lineHeight: 1.4 }}>
                The underlying forensic variables, pillar evidence and established models have been evaluated. Final weighted EFS scoring is pending empirical calibration.
              </Typography>
            </Box>
          </Stack>
        </Grid>

        {/* Core Metric Cards */}
        <Grid size={{ xs: 12, md: 7 }}>
          <Grid container spacing={1.5}>
            <Grid size={{ xs: 6, sm: 3 }}>
              <Box sx={{ p: 2, bgcolor: '#f8fafc', borderRadius: 2, border: '1px solid #e2e8f0' }}>
                <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>
                  Risk Level
                </Typography>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#b45309', mt: 0.5 }}>
                  Pending
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Weighted Score Withheld
                </Typography>
              </Box>
            </Grid>

            <Grid size={{ xs: 6, sm: 3 }}>
              <Box sx={{ p: 2, bgcolor: '#f8fafc', borderRadius: 2, border: '1px solid #e2e8f0' }}>
                <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>
                  Confidence
                </Typography>

                <Stack direction="row" spacing={0.5} alignItems="center" sx={{ mt: 0.5 }}>
                  <ShieldOutlinedIcon sx={{ fontSize: 18, color: '#0284c7' }} />
                  <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#0369a1' }}>
                    {overall.confidence.toFixed(1)}%
                  </Typography>
                </Stack>
                <Typography variant="caption" color="text.secondary">
                  Data Quality Score
                </Typography>
              </Box>
            </Grid>

            <Grid size={{ xs: 6, sm: 3 }}>
              <Box sx={{ p: 2, bgcolor: '#f8fafc', borderRadius: 2, border: '1px solid #e2e8f0' }}>
                <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>
                  Variables Evaluated
                </Typography>

                <Stack direction="row" spacing={0.5} alignItems="center" sx={{ mt: 0.5 }}>
                  <VariablesIcon sx={{ fontSize: 18, color: '#4f46e5' }} />
                  <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#4338ca' }}>
                    {variablesAvailable} / {variablesEvaluated}
                  </Typography>
                </Stack>
                <Typography variant="caption" color="text.secondary">
                  Methodology Inputs
                </Typography>
              </Box>
            </Grid>

            <Grid size={{ xs: 6, sm: 3 }}>
              <Box sx={{ p: 2, bgcolor: '#f8fafc', borderRadius: 2, border: '1px solid #e2e8f0' }}>
                <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>
                  Rules Triggered
                </Typography>

                <Stack direction="row" spacing={0.5} alignItems="center" sx={{ mt: 0.5 }}>
                  {rulesTriggered > 0 ? (
                    <WarningAmberIcon sx={{ fontSize: 18, color: '#dc2626' }} />
                  ) : (
                    <RulesIcon sx={{ fontSize: 18, color: '#16a34a' }} />
                  )}
                  <Typography
                    variant="subtitle1"
                    sx={{ fontWeight: 800, color: rulesTriggered > 0 ? '#b91c1c' : '#15803d' }}
                  >
                    {rulesTriggered} / {rulesEvaluated}
                  </Typography>
                </Stack>
                <Typography variant="caption" color="text.secondary">
                  Forensic Red Flags
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Card>
  )
}
