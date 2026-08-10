import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Alert, Box, Button, Card, CardContent, Chip, CircularProgress,
  Divider, Stack, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Tooltip, Typography
} from '@mui/material'
import { ArrowBack, Assessment, OpenInNew } from '@mui/icons-material'
import { CompanyService } from '../services/api/assessmentService'
import { AssessmentService } from '../services/api/assessmentService'
import type { CompanyRecord, AssessmentListItem } from '../types/efs'

export function CompanyPage() {
  const { companyId } = useParams<{ companyId: string }>()
  const navigate = useNavigate()

  const [company, setCompany] = useState<CompanyRecord | null>(null)
  const [assessments, setAssessments] = useState<AssessmentListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!companyId) return
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const [co, asms] = await Promise.all([
          CompanyService.getCompany(companyId),
          AssessmentService.getCompanyAssessments(companyId),
        ])
        setCompany(co)
        setAssessments(asms)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load company data')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [companyId])

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
    return item.overall_score !== null
      ? <Typography fontWeight={700}>{item.overall_score.toFixed(1)}</Typography>
      : <Typography color="text.secondary">—</Typography>
  }

  const formatDate = (iso: string | null) => {
    if (!iso) return '—'
    return new Date(iso).toLocaleDateString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric',
    })
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">{error}</Alert>
        <Button startIcon={<ArrowBack />} onClick={() => navigate(-1)} sx={{ mt: 2 }}>
          Go Back
        </Button>
      </Box>
    )
  }

  if (!company) return null

  const latestAssessment = assessments[0] ?? null

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1400, mx: 'auto' }}>
      <Button startIcon={<ArrowBack />} onClick={() => navigate(-1)} sx={{ mb: 2 }}>
        Back
      </Button>

      {/* Company Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack direction="row" alignItems="center" spacing={2}>
            <Assessment sx={{ fontSize: 48, color: 'primary.main', opacity: 0.7 }} />
            <Box>
              <Typography variant="h4" fontWeight={700}>{company.legal_name}</Typography>
              {company.display_name && company.display_name !== company.legal_name && (
                <Typography color="text.secondary">{company.display_name}</Typography>
              )}
              <Stack direction="row" spacing={1} sx={{ mt: 1 }} flexWrap="wrap">
                {company.ticker && <Chip label={company.ticker} size="small" variant="outlined" />}
                {company.exchange && <Chip label={company.exchange} size="small" variant="outlined" />}
                {company.country && <Chip label={company.country} size="small" />}
                {company.industry && (
                  <Chip label={company.industry} size="small" color="primary" variant="outlined" />
                )}
              </Stack>
            </Box>
          </Stack>
        </CardContent>
      </Card>

      {/* Latest Assessment */}
      {latestAssessment && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight={700} gutterBottom>Latest Assessment</Typography>
            <Divider sx={{ mb: 2 }} />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={3} justifyContent="space-between">
              <Box>
                <Typography variant="caption" color="text.secondary">ANALYSIS ID</Typography>
                <Typography fontFamily="monospace" fontWeight={700}>{latestAssessment.analysis_id}</Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">EFS SCORE</Typography>
                <Box>{scoreDisplay(latestAssessment)}</Box>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">CONFIDENCE</Typography>
                <Typography fontWeight={700}>
                  {latestAssessment.confidence_score !== null
                    ? `${latestAssessment.confidence_score.toFixed(0)}%`
                    : '—'}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">RULES TRIGGERED</Typography>
                <Typography fontWeight={700}>{latestAssessment.rules_triggered ?? '—'}</Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">DATE</Typography>
                <Typography>{formatDate(latestAssessment.completed_at || latestAssessment.created_at)}</Typography>
              </Box>
              <Box>
                <Button
                  variant="contained"
                  size="small"
                  startIcon={<OpenInNew />}
                  onClick={() => navigate(`/assessments/${latestAssessment.analysis_id}`)}
                >
                  View Assessment
                </Button>
              </Box>
            </Stack>
          </CardContent>
        </Card>
      )}

      {/* Assessment History */}
      <Card>
        <CardContent sx={{ p: 0 }}>
          <Box sx={{ px: 2.5, pt: 2.5, pb: 1.5 }}>
            <Typography variant="h6" fontWeight={700}>Assessment History</Typography>
            <Typography variant="body2" color="text.secondary">
              {assessments.length} assessment{assessments.length !== 1 ? 's' : ''} — each is an immutable forensic snapshot.
            </Typography>
          </Box>

          {assessments.length === 0 ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <Typography color="text.secondary">No assessments found for this company.</Typography>
            </Box>
          ) : (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    {['ANALYSIS ID', 'STATUS', 'SCORE', 'CONFIDENCE', 'RULES TRIGGERED', 'VERSION', 'DATE', ''].map((h) => (
                      <TableCell key={h} sx={{ fontWeight: 700, fontSize: '0.7rem' }}>{h}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {assessments.map((item) => (
                    <TableRow
                      key={item.id}
                      hover
                      sx={{ cursor: 'pointer' }}
                      onClick={() => navigate(`/assessments/${item.analysis_id}`)}
                    >
                      <TableCell sx={{ fontFamily: 'monospace', fontWeight: 600 }}>{item.analysis_id}</TableCell>
                      <TableCell>
                        <Chip
                          label={item.assessment_status}
                          color={item.assessment_status === 'COMPLETED' ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{scoreDisplay(item)}</TableCell>
                      <TableCell>
                        {item.confidence_score !== null ? `${item.confidence_score.toFixed(0)}%` : '—'}
                      </TableCell>
                      <TableCell>{item.rules_triggered ?? '—'}</TableCell>
                      <TableCell><Chip label={`v${item.efs_version}`} size="small" variant="outlined" /></TableCell>
                      <TableCell>{formatDate(item.completed_at || item.created_at)}</TableCell>
                      <TableCell>
                        <Tooltip title="View assessment" onClick={(e) => { e.stopPropagation(); navigate(`/assessments/${item.analysis_id}`) }}>
                          <OpenInNew fontSize="small" sx={{ cursor: 'pointer', color: 'text.secondary' }} />
                        </Tooltip>
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
