import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box, Button, Card, CardContent, Chip, CircularProgress,
  IconButton, InputAdornment, Pagination, Stack, Table,
  TableBody, TableCell, TableContainer, TableHead, TableRow,
  TextField, Tooltip, Typography, Alert
} from '@mui/material'
import {
  FilterList, OpenInNew, Refresh, Search, VisibilityOutlined
} from '@mui/icons-material'
import { EmptyState } from '../components/feedback/FeedbackComponents'
import { AssessmentService } from '../services/api/assessmentService'
import type { AssessmentListItem } from '../types/efs'

export function History() {
  const navigate = useNavigate()
  const [items, setItems] = useState<AssessmentListItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const limit = 20

  const fetchAssessments = async (p: number) => {
    setLoading(true)
    setError(null)
    try {
      const data = await AssessmentService.listAssessments(p, limit)
      setItems(data.items)
      setTotal(data.total)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load assessment history')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAssessments(page)
  }, [page])

  const filtered = items.filter((row) =>
    `${row.analysis_id} ${row.assessment_status}`.toLowerCase().includes(query.toLowerCase())
  )

  const totalPages = Math.max(1, Math.ceil(total / limit))

  const scoreDisplay = (item: AssessmentListItem) => {
    if (item.score_status === 'CALIBRATION_PENDING') {
      return (
        <Chip
          label="Calibration Pending"
          size="small"
          variant="outlined"
          sx={{ fontSize: '0.7rem', color: 'warning.main', borderColor: 'warning.main' }}
        />
      )
    }
    if (item.overall_score !== null) {
      return <Typography variant="body2" fontWeight={800}>{item.overall_score.toFixed(1)}</Typography>
    }
    return <Typography variant="body2" color="text.secondary">—</Typography>
  }

  const statusColor = (status: string) => {
    if (status === 'COMPLETED') return 'success'
    if (status === 'RUNNING') return 'info'
    if (status === 'FAILED') return 'error'
    return 'default'
  }

  const confidenceDisplay = (item: AssessmentListItem) => {
    if (item.confidence_score === null) return '—'
    return `${item.confidence_score.toFixed(0)}% (${item.confidence_level || ''})`
  }

  const formatDate = (iso: string | null) => {
    if (!iso) return '—'
    return new Date(iso).toLocaleDateString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric',
    })
  }

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1400, mx: 'auto' }}>
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h1">Assessment History</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.5 }}>
            Persisted EFS™ forensic assessments — immutable snapshots from Neon PostgreSQL.
          </Typography>
        </Box>
        <Tooltip title="Refresh">
          <IconButton onClick={() => fetchAssessments(page)} disabled={loading}>
            <Refresh />
          </IconButton>
        </Tooltip>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Card>
        <CardContent sx={{ p: 0 }}>
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            justifyContent="space-between"
            spacing={1.5}
            sx={{ p: 2.5 }}
          >
            <TextField
              size="small"
              placeholder="Filter by analysis ID or status"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search fontSize="small" />
                  </InputAdornment>
                ),
              }}
              sx={{ minWidth: 280 }}
            />
            <Button variant="outlined" startIcon={<FilterList />}>Filter</Button>
          </Stack>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
              <CircularProgress />
            </Box>
          ) : filtered.length === 0 ? (
            <Box sx={{ p: 4 }}>
              <EmptyState variant="history" />
            </Box>
          ) : (
            <>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      {[
                        'ANALYSIS ID', 'STATUS', 'EFS SCORE', 'RISK LEVEL',
                        'CONFIDENCE', 'RULES TRIGGERED', 'EFS VERSION', 'DATE', 'ACTIONS'
                      ].map((head) => (
                        <TableCell key={head} sx={{ fontWeight: 700, fontSize: '0.7rem', letterSpacing: 0.5 }}>
                          {head}
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filtered.map((row) => (
                      <TableRow
                        key={row.id}
                        hover
                        sx={{ cursor: 'pointer' }}
                        onClick={() => navigate(`/assessments/${row.analysis_id}`)}
                      >
                        <TableCell sx={{ fontWeight: 700, fontFamily: 'monospace', fontSize: '0.8rem' }}>
                          {row.analysis_id}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={row.assessment_status}
                            color={statusColor(row.assessment_status) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{scoreDisplay(row)}</TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {row.risk_level || '—'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">{confidenceDisplay(row)}</Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight={700}>
                            {row.rules_triggered ?? '—'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip label={`v${row.efs_version}`} size="small" variant="outlined" />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {formatDate(row.completed_at || row.created_at)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Stack direction="row" onClick={(e) => e.stopPropagation()}>
                            <Tooltip title="View assessment detail">
                              <IconButton
                                size="small"
                                onClick={() => navigate(`/assessments/${row.analysis_id}`)}
                              >
                                <VisibilityOutlined fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="View report">
                              <IconButton
                                size="small"
                                onClick={() => navigate(`/assessments/${row.analysis_id}/report`)}
                              >
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

              <Stack alignItems="center" sx={{ p: 2 }}>
                <Pagination
                  count={totalPages}
                  page={page}
                  onChange={(_, p) => setPage(p)}
                  color="primary"
                />
                <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                  {total} total assessment{total !== 1 ? 's' : ''}
                </Typography>
              </Stack>
            </>
          )}
        </CardContent>
      </Card>
    </Box>
  )
}
