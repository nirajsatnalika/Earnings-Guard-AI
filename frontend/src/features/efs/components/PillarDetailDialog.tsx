import {
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import type { EFSVariable, PillarResult } from '../../../types/efs'

interface PillarDetailDialogProps {
  pillar: PillarResult | null
  open: boolean
  onClose: () => void
}

function formatRawValue(val: number | null, unit: string): string {
  if (val === null || val === undefined) return '—'
  if (unit === 'Days') return `${val.toFixed(1)} days`
  if (unit === 'Ratio' || unit === 'Index') return val.toFixed(4)
  if (unit === 'Growth rate' || unit === 'Percentage points' || unit === '%') return `${(val * (unit === 'Growth rate' ? 100 : 1)).toFixed(2)}%`
  return `${val}`
}

function getScoreChipColor(score: number | null): 'error' | 'warning' | 'info' | 'success' | 'default' {
  if (score === null) return 'default'
  if (score <= 25) return 'error'
  if (score <= 50) return 'warning'
  if (score <= 75) return 'info'
  return 'success'
}

export function PillarDetailDialog({ pillar, open, onClose }: PillarDetailDialogProps) {
  if (!pillar) return null

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle sx={{ p: 3, pb: 1, bgcolor: '#0f172a', color: '#ffffff' }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <Stack direction="row" spacing={1} alignItems="center">
              <Chip label={pillar.pillar_id} size="small" sx={{ bgcolor: '#38bdf8', color: '#0f172a', fontWeight: 800 }} />
              <Typography variant="h6" sx={{ fontWeight: 700, color: '#ffffff' }}>
                {pillar.pillar_name}
              </Typography>
            </Stack>
            <Typography variant="body2" sx={{ color: '#94a3b8', mt: 0.5 }}>
              Pillar Variable Evidence & Forensic Scoring Bands ({pillar.variables_available} Available / {pillar.variables_evaluated} Evaluated)
            </Typography>
          </Box>

          <Button onClick={onClose} sx={{ color: '#94a3b8', minWidth: 'auto' }}>
            <CloseIcon />
          </Button>
        </Stack>
      </DialogTitle>

      <DialogContent sx={{ p: 3, bgcolor: '#f8fafc' }}>
        <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #cbd5e1', borderRadius: 2 }}>
          <Table size="medium">
            <TableHead sx={{ bgcolor: '#f1f5f9' }}>
              <TableRow>
                <TableCell sx={{ fontWeight: 700, color: '#334155' }}>Variable ID</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#334155' }}>Variable Name</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#334155' }}>Raw Value</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#334155' }}>Unit</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#334155' }}>Score / Band</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#334155' }}>Status</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#334155' }}>Source Fields</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {pillar.variables && pillar.variables.length > 0 ? (
                pillar.variables.map((v: EFSVariable) => (
                  <TableRow key={v.variable_id} hover>
                    <TableCell sx={{ fontFamily: 'monospace', fontWeight: 700, color: '#0f172a' }}>
                      {v.variable_id}
                    </TableCell>
                    <TableCell sx={{ fontWeight: 600, color: '#1e293b' }}>
                      {v.variable_name}
                    </TableCell>
                    <TableCell sx={{ fontFamily: 'monospace', fontWeight: 700, color: v.raw_value === null ? '#94a3b8' : '#0f172a' }}>
                      {formatRawValue(v.raw_value, v.unit)}
                    </TableCell>
                    <TableCell sx={{ color: '#64748b', fontSize: '0.8rem' }}>
                      {v.unit}
                    </TableCell>
                    <TableCell>
                      {v.score !== null ? (
                        <Chip
                          label={`${v.score} / 100 (${v.scoring_band || ''})`}
                          size="small"
                          color={getScoreChipColor(v.score)}
                          sx={{ fontWeight: 700 }}
                        />
                      ) : (
                        <Chip label="—" size="small" variant="outlined" sx={{ color: '#94a3b8' }} />
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={v.data_status}
                        size="small"
                        color={v.data_status === 'AVAILABLE' ? 'success' : 'default'}
                        variant={v.data_status === 'AVAILABLE' ? 'filled' : 'outlined'}
                        sx={{ fontWeight: 700, fontSize: '0.7rem' }}
                      />
                    </TableCell>
                    <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.75rem', color: '#475569' }}>
                      {v.source_fields ? v.source_fields.join(', ') : '—'}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4, color: '#64748b' }}>
                    No variable records returned for this pillar.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2, bgcolor: '#f1f5f9', borderTop: '1px solid #cbd5e1' }}>
        <Button onClick={onClose} variant="contained" sx={{ bgcolor: '#0f172a', textTransform: 'none' }}>
          Close Drill-Down
        </Button>
      </DialogActions>
    </Dialog>
  )
}
