import { Box, Chip, Paper, Stack, Typography } from '@mui/material'
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser'
import CheckCircleOutline from '@mui/icons-material/CheckCircleOutline'

interface AssessmentHeaderProps {
  companyName?: string
  ticker?: string
  assessmentId: string
  analysisId: string
  efsVersion: string
  status: string
  timestamp?: string
}

export function AssessmentHeader({
  companyName = 'ABC Limited',
  ticker = 'ABCL',
  assessmentId,
  analysisId,
  efsVersion,
  status,
  timestamp,
}: AssessmentHeaderProps) {
  const formattedDate = new Date(timestamp || Date.now()).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short',
  })

  return (
    <Paper
      elevation={0}
      sx={{
        p: { xs: 2.5, md: 3.5 },
        mb: 3,
        borderRadius: 2,
        border: '1px solid #e2e8f0',
        background: 'linear-gradient(180deg, #1e293b 0%, #0f172a 100%)',
        color: '#f8fafc',
      }}
    >
      <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" alignItems={{ md: 'center' }} spacing={2}>
        <Box>
          <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 1 }}>
            <VerifiedUserIcon sx={{ color: '#38bdf8', fontSize: 28 }} />
            <Typography variant="h5" sx={{ fontWeight: 800, letterSpacing: '-0.02em', color: '#ffffff' }}>
              EarningsGuard™ AI
            </Typography>
            <Typography variant="body2" sx={{ color: '#94a3b8', fontWeight: 600 }}>
              Financial Forensics Assessment
            </Typography>
          </Stack>

          <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
            <Typography variant="h4" sx={{ fontWeight: 700, color: '#f8fafc' }}>
              {companyName} {ticker && <Typography component="span" variant="h6" sx={{ color: '#cbd5e1', fontWeight: 400 }}>({ticker})</Typography>}
            </Typography>
            <Chip
              icon={<CheckCircleOutline sx={{ color: '#34d399 !important' }} />}
              label={status === 'COMPLETED' ? 'Assessment Complete' : status}
              sx={{
                bgcolor: 'rgba(52, 211, 153, 0.15)',
                color: '#34d399',
                fontWeight: 700,
                fontSize: '0.8rem',
                border: '1px solid rgba(52, 211, 153, 0.3)',
              }}
            />
          </Stack>
        </Box>

        <Stack direction={{ xs: 'row', md: 'column' }} spacing={{ xs: 3, md: 1 }} alignItems={{ md: 'flex-end' }}>
          <Box sx={{ textAlign: { md: 'right' } }}>
            <Typography variant="caption" sx={{ color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Assessment ID / Analysis ID
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 600, color: '#e2e8f0' }}>
              {assessmentId} ({analysisId})
            </Typography>
          </Box>

          <Box sx={{ textAlign: { md: 'right' } }}>
            <Typography variant="caption" sx={{ color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Date & EFS Version
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 500, color: '#cbd5e1' }}>
              {formattedDate} · v{efsVersion}
            </Typography>
          </Box>
        </Stack>
      </Stack>
    </Paper>
  )
}
