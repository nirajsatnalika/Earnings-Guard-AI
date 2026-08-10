import { Box, Paper, Stack, Typography } from '@mui/material'
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined'

export function CalibrationNotice() {
  return (
    <Paper
      elevation={0}
      sx={{
        p: 2.5,
        mb: 3,
        borderRadius: 2,
        bgcolor: '#eff6ff',
        border: '1px solid #bfdbfe',
      }}
    >
      <Stack direction="row" spacing={2} alignItems="flex-start">
        <InfoOutlinedIcon sx={{ color: '#1d4ed8', mt: 0.2 }} />
        <Box>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#1e40af' }}>
            Why isn't there an EFS™ score yet?
          </Typography>
          <Typography variant="body2" sx={{ color: '#1e3a8a', mt: 0.5, lineHeight: 1.5 }}>
            EFS™ v1.0 has completed deterministic financial and forensic analysis. Final weighted scoring is intentionally withheld until the methodology is empirically calibrated against historical cases. This prevents false precision.
          </Typography>
        </Box>
      </Stack>
    </Paper>
  )
}
