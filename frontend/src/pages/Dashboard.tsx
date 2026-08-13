import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  IconButton,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
} from '@mui/material'
import {
  AddOutlined,
  OpenInNew,
  PlayCircleOutline,
  Refresh,
  ShieldOutlined,
  VisibilityOutlined,
} from '@mui/icons-material'
import { AssessmentService } from '../services/api/assessmentService'
import { EFSService } from '../services/api/efsService'
import type { AssessmentListItem } from '../types/efs'
import { useToast } from '../services/feedback'

const SAMPLE_DEMO_INPUT = {
  methodology_version: '1.0',
  statement_flags: {
    has_cash_flow_statement: true,
    has_balance_sheet: true,
    has_income_statement: true,
  },
  raw_variables: {
    revenue: 500000.0,
    prior_revenue: 450000.0,
    receivables: 80000.0,
    prior_receivables: 65000.0,
    cfo: 60000.0,
    pat: 45000.0,
    cogs: 300000.0,
    inventory: 50000.0,
    payables: 40000.0,
    total_assets: 600000.0,
    prior_total_assets: 550000.0,
    depreciation: 20000.0,
    total_debt: 150000.0,
    equity: 350000.0,
    ebit: 70000.0,
  },
}

export function Dashboard() {
  const navigate = useNavigate()
  const toast = useToast()
  const [assessments, setAssessments] = useState<AssessmentListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [demoLoading, setDemoLoading] = useState(false)

  const fetchRecent = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await AssessmentService.listAssessments(1, 10)
      setAssessments(data.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load recent assessments')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRecent()
  }, [])

  const handleLoadDemoAssessment = async () => {
    setDemoLoading(true)
    try {
      const demoId = `demo_${Date.now()}`
      await EFSService.getAssessment(demoId, SAMPLE_DEMO_INPUT)
      toast.notifySuccess('Demo assessment created successfully!')
      navigate(`/assessments/${demoId}`)
    } catch (err) {
      toast.notifyError(err instanceof Error ? err.message : 'Failed to create demo assessment')
    } finally {
      setDemoLoading(false)
    }
  }

  const formatDate = (iso: string | null) => {
    if (!iso) return '—'
    return new Date(iso).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    })
  }

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1400, mx: 'auto' }}>
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        justifyContent="space-between"
        alignItems={{ sm: 'center' }}
        spacing={2}
        sx={{ mb: 3.5 }}
      >
        <Box>
          <Stack direction="row" alignItems="center" spacing={1.5}>
            <Typography variant="h1">EarningsGuard™ AI</Typography>
            <Chip label="EFS Engine v1.0" color="primary" size="small" variant="outlined" />
          </Stack>
          <Typography color="text.secondary" sx={{ mt: 0.5 }}>
            Forensic Financial Intelligence — Institutional Earnings Quality & Manipulation Detection
          </Typography>
        </Box>
        <Stack direction="row" spacing={1.5} alignItems="center">
          <Button
            variant="outlined"
            color="secondary"
            startIcon={<PlayCircleOutline />}
            onClick={handleLoadDemoAssessment}
            disabled={demoLoading}
          >
            {demoLoading ? 'Loading Demo…' : 'Load Demo Assessment'}
            <Chip
              label="DEMO DATA"
              size="small"
              color="warning"
              sx={{ ml: 1, height: 20, fontSize: '0.65rem', fontWeight: 800 }}
            />
          </Button>
          <Button
            variant="contained"
            startIcon={<AddOutlined />}
            onClick={() => navigate('/analysis/new')}
          >
            New Assessment
          </Button>
        </Stack>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} action={<Button color="inherit" size="small" onClick={fetchRecent}>Retry</Button>}>
          {error}
        </Alert>
      )}

      <Card>
        <CardContent sx={{ p: 2.5 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Box>
              <Typography variant="h3">Recent Assessments</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                Persisted forensic snapshots evaluated by the EFS™ deterministic engine
              </Typography>
            </Box>
            <Tooltip title="Refresh">
              <IconButton onClick={fetchRecent} disabled={loading}>
                <Refresh fontSize="small" />
              </IconButton>
            </Tooltip>
          </Stack>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
              <CircularProgress size={36} />
            </Box>
          ) : assessments.length === 0 ? (
            <Box
              sx={{
                py: 6,
                px: 2,
                textAlign: 'center',
                bgcolor: 'rgba(248, 250, 252, 0.6)',
                borderRadius: 2,
                border: '1px dashed #cbd5e1',
              }}
            >
              <ShieldOutlined sx={{ fontSize: 48, color: 'text.secondary', mb: 1.5, opacity: 0.5 }} />
              <Typography variant="h6" fontWeight={700} sx={{ mb: 0.5 }}>
                No assessments yet
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 450, mx: 'auto' }}>
                Start your first forensic financial assessment to evaluate earnings quality, accrual anomalies, and statement manipulation signals.
              </Typography>
              <Stack direction="row" spacing={2} justifyContent="center">
                <Button variant="contained" onClick={() => navigate('/analysis/new')}>
                  Create Assessment
                </Button>
                <Button
                  variant="outlined"
                  onClick={handleLoadDemoAssessment}
                  disabled={demoLoading}
                >
                  Load Demo Assessment
                  <Chip
                    label="DEMO DATA"
                    size="small"
                    color="warning"
                    sx={{ ml: 1, height: 18, fontSize: '0.6rem', fontWeight: 800 }}
                  />
                </Button>
              </Stack>
            </Box>
          ) : (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.7rem' }}>ANALYSIS ID</TableCell>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.7rem' }}>ASSESSMENT STATUS</TableCell>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.7rem' }}>EFS STATUS</TableCell>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.7rem' }}>VARIABLES</TableCell>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.7rem' }}>RULES TRIGGERED</TableCell>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.7rem' }}>DATE</TableCell>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.7rem' }}>ACTIONS</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {assessments.map((row) => (
                    <TableRow
                      key={row.id}
                      hover
                      sx={{ cursor: 'pointer' }}
                      onClick={() => navigate(`/assessments/${row.analysis_id}`)}
                    >
                      <TableCell sx={{ fontWeight: 700, fontFamily: 'monospace', fontSize: '0.82rem' }}>
                        {row.analysis_id}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={row.assessment_status}
                          color={row.assessment_status === 'COMPLETED' ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label="Calibration Pending"
                          size="small"
                          variant="outlined"
                          sx={{ fontSize: '0.7rem', color: 'warning.main', borderColor: 'warning.main' }}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight={650}>
                          {row.variables_evaluated ?? 95} evaluated
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight={700}>
                          {row.rules_triggered ?? 0}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{formatDate(row.completed_at || row.created_at)}</Typography>
                      </TableCell>
                      <TableCell>
                        <Stack direction="row" onClick={(e) => e.stopPropagation()}>
                          <Tooltip title="View Assessment">
                            <IconButton size="small" onClick={() => navigate(`/assessments/${row.analysis_id}`)}>
                              <VisibilityOutlined fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="View Report PDF">
                            <IconButton size="small" onClick={() => navigate(`/assessments/${row.analysis_id}/report`)}>
                              <OpenInNew fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
    </Box>
  )
}

