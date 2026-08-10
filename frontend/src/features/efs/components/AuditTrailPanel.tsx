import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Chip,
  Grid,
  Stack,
  Typography,
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import SecurityIcon from '@mui/icons-material/Security'
import type { AuditTrail } from '../../../types/efs'

interface AuditTrailPanelProps {
  auditTrail: AuditTrail
}

export function AuditTrailPanel({ auditTrail }: AuditTrailPanelProps) {
  if (!auditTrail) return null

  return (
    <Accordion
      elevation={0}
      sx={{
        mb: 4,
        borderRadius: '8px !important',
        border: '1px solid #cbd5e1',
        '&:before': { display: 'none' },
      }}
    >
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Stack direction="row" spacing={1.5} alignItems="center">
          <SecurityIcon sx={{ color: '#64748b' }} />
          <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#334155' }}>
            Regulatory & Forensic Audit Trail
          </Typography>
          <Chip label="v1.0 Immutable" size="small" variant="outlined" sx={{ fontWeight: 700, fontSize: '0.7rem' }} />
        </Stack>
      </AccordionSummary>

      <AccordionDetails sx={{ p: 3, bg: '#f8fafc', borderTop: '1px solid #e2e8f0' }}>
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ p: 1.5, bgcolor: '#ffffff', borderRadius: 1.5, border: '1px solid #e2e8f0' }}>
              <Typography variant="caption" color="text.secondary">
                Assessment ID
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 700, color: '#0f172a' }}>
                {auditTrail.assessment_id}
              </Typography>
            </Box>
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ p: 1.5, bgcolor: '#ffffff', borderRadius: 1.5, border: '1px solid #e2e8f0' }}>
              <Typography variant="caption" color="text.secondary">
                Analysis ID
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 700, color: '#0f172a' }}>
                {auditTrail.analysis_id}
              </Typography>
            </Box>
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ p: 1.5, bgcolor: '#ffffff', borderRadius: 1.5, border: '1px solid #e2e8f0' }}>
              <Typography variant="caption" color="text.secondary">
                Methodology / Engine Version
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 700, color: '#0f172a' }}>
                EFS v{auditTrail.efs_version} · Engine v{auditTrail.engine_version}
              </Typography>
            </Box>
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ p: 1.5, bgcolor: '#ffffff', borderRadius: 1.5, border: '1px solid #e2e8f0' }}>
              <Typography variant="caption" color="text.secondary">
                Timestamp (UTC)
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 600, color: '#0f172a' }}>
                {auditTrail.timestamp}
              </Typography>
            </Box>
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ p: 1.5, bgcolor: '#ffffff', borderRadius: 1.5, border: '1px solid #e2e8f0' }}>
              <Typography variant="caption" color="text.secondary">
                Variables Evaluated
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 700, color: '#0f172a' }}>
                {auditTrail.variables_available} Available / {auditTrail.variables_evaluated} Evaluated
              </Typography>
            </Box>
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ p: 1.5, bgcolor: '#ffffff', borderRadius: 1.5, border: '1px solid #e2e8f0' }}>
              <Typography variant="caption" color="text.secondary">
                Rules Evaluated
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 700, color: '#0f172a' }}>
                {auditTrail.rules_triggered} Triggered / {auditTrail.rules_evaluated} Evaluated
              </Typography>
            </Box>
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ p: 1.5, bgcolor: '#ffffff', borderRadius: 1.5, border: '1px solid #e2e8f0' }}>
              <Typography variant="caption" color="text.secondary">
                Rulebook Version
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 700, color: '#0f172a' }}>
                Rulebook v{auditTrail.rulebook_version} · Scoring v{auditTrail.scoring_version}
              </Typography>
            </Box>
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ p: 1.5, bgcolor: '#ffffff', borderRadius: 1.5, border: '1px solid #e2e8f0' }}>
              <Typography variant="caption" color="text.secondary">
                Calculation Time
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 700, color: '#0f172a' }}>
                {auditTrail.calculation_time_ms} ms
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </AccordionDetails>
    </Accordion>
  )
}
