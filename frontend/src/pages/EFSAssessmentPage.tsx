import { useCallback, useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Paper,
  Typography,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import RefreshIcon from '@mui/icons-material/Refresh'

import { EFSService } from '../services/api/efsService'
import type { EFSResponse, PillarResult } from '../types/efs'

import { AssessmentHeader } from '../features/efs/components/AssessmentHeader'
import { AssessmentStatus } from '../features/efs/components/AssessmentStatus'
import { CalibrationNotice } from '../features/efs/components/CalibrationNotice'
import { ExecutiveSummary } from '../features/efs/components/ExecutiveSummary'
import { PillarsOverview } from '../features/efs/components/PillarsOverview'
import { PillarDetailDialog } from '../features/efs/components/PillarDetailDialog'
import { EstablishedModelsPanel } from '../features/efs/components/EstablishedModelsPanel'
import { ForensicFindingsPanel } from '../features/efs/components/ForensicFindingsPanel'
import { RedFlagsPanel } from '../features/efs/components/RedFlagsPanel'
import { ManagementQuestionsPanel } from '../features/efs/components/ManagementQuestionsPanel'
import { ConfidencePanel } from '../features/efs/components/ConfidencePanel'
import { AuditTrailPanel } from '../features/efs/components/AuditTrailPanel'
import { AINarrativePanel } from '../features/efs/components/AINarrativePanel'

export function EFSAssessmentPage() {
  const { analysisId = 'sample_analysis_001' } = useParams<{ analysisId: string }>()
  const navigate = useNavigate()

  const [assessment, setAssessment] = useState<EFSResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [notFound, setNotFound] = useState<boolean>(false)
  const [selectedPillar, setSelectedPillar] = useState<PillarResult | null>(null)

  const fetchAssessment = useCallback(async () => {
    setLoading(true)
    setError(null)
    setNotFound(false)
    try {
      // Phase 5: POST creates + persists. The EFS API returns the full assessment.
      // For navigation from history (/assessments/:analysisId), we still POST to retrieve
      // (idempotent — existing completed assessments are not re-run server-side).
      const data = await EFSService.getAssessment(analysisId)
      setAssessment(data)
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to load EFS assessment.'
      // 404 means assessment does not exist — show "Not Found", do NOT silently re-run engine
      if (msg.includes('404') || msg.includes('not found') || msg.toLowerCase().includes('no completed assessment')) {
        setNotFound(true)
      } else {
        setError(msg)
      }
    } finally {
      setLoading(false)
    }
  }, [analysisId])

  useEffect(() => {
    fetchAssessment()
  }, [fetchAssessment])


  if (loading) {
    return (
      <Box
        sx={{
          minHeight: '80vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          p: 4,
        }}
      >
        <CircularProgress size={48} sx={{ color: '#0f172a', mb: 2.5 }} />
        <Typography variant="h6" sx={{ fontWeight: 700, color: '#0f172a' }}>
          Executing EFS™ Forensics Pipeline...
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Evaluating 95 methodology variables and 110 forensic rules for Analysis ID: {analysisId}
        </Typography>
      </Box>
    )
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Alert
          severity="error"
          action={
            <Button color="inherit" size="small" startIcon={<RefreshIcon />} onClick={fetchAssessment}>
              Retry
            </Button>
          }
          sx={{ mb: 3 }}
        >
          <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
            Unable to Load EFS™ Assessment
          </Typography>
          <Typography variant="body2">{error}</Typography>
        </Alert>
        <Button startIcon={<ArrowBackIcon />} variant="outlined" onClick={() => navigate('/')}>
          Return to Dashboard
        </Button>
      </Container>
    )
  }

  if (notFound) {
    return (
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Paper elevation={0} sx={{ p: 4, textAlign: 'center', border: '1px solid #cbd5e1', borderRadius: 2 }}>
          <Typography variant="h5" sx={{ color: '#0f172a', fontWeight: 700, mb: 1 }}>
            Assessment Not Found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            No completed assessment found for: <code>{analysisId}</code>
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            To view an assessment, it must first be submitted via the assessment workflow.
            The engine will not re-run automatically.
          </Typography>
          <Button variant="contained" onClick={() => navigate('/analysis/new')} sx={{ mr: 1 }}>
            Start New Assessment
          </Button>
          <Button variant="outlined" onClick={() => navigate('/history')}>
            View History
          </Button>
        </Paper>
      </Container>
    )
  }

  if (!assessment) {

    return (
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Paper elevation={0} sx={{ p: 4, textAlign: 'center', border: '1px solid #cbd5e1', borderRadius: 2 }}>
          <Typography variant="h6" sx={{ color: '#475569', mb: 1 }}>
            No Assessment Record Found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Assessment could not evaluate variables because required financial/disclosure data was unavailable.
          </Typography>
          <Button variant="contained" onClick={() => navigate('/analysis/new')}>
            Start New Assessment
          </Button>
        </Paper>
      </Container>
    )
  }

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1440, mx: 'auto' }}>
      {/* 1. Assessment Header */}
      <AssessmentHeader
        companyName={assessment.company_name || 'Infosys Ltd.'}
        ticker={assessment.ticker || 'INFY'}
        assessmentId={assessment.assessment_id}
        analysisId={assessment.analysis_id}
        efsVersion={assessment.efs_version}
        status={assessment.status}
        timestamp={assessment.audit_trail?.timestamp}
      />

      {/* 2. Overall Status */}
      <AssessmentStatus
        overall={assessment.overall}
        variablesEvaluated={assessment.audit_trail?.variables_evaluated || 95}
        variablesAvailable={assessment.audit_trail?.variables_available || 0}
        rulesEvaluated={assessment.audit_trail?.rules_evaluated || 110}
        rulesTriggered={assessment.audit_trail?.rules_triggered || 0}
      />

      {/* 3. Calibration Notice */}
      <CalibrationNotice />

      {/* 4. Executive Forensic Summary */}
      <ExecutiveSummary
        pillars={assessment.pillars}
        findings={assessment.forensic_findings}
        limitations={assessment.limitations}
      />

      {/* 5. Key Forensic Red Flags */}
      <RedFlagsPanel
        redFlags={assessment.red_flags}
        findings={assessment.forensic_findings}
      />

      {/* 6. Seven Pillars View */}
      <PillarsOverview
        pillars={assessment.pillars}
        onSelectPillar={(pillar) => setSelectedPillar(pillar)}
      />

      {/* 7. Established Models */}
      <EstablishedModelsPanel models={assessment.established_models} />

      {/* 8. Forensic Findings Rulebook */}
      <ForensicFindingsPanel findings={assessment.forensic_findings} />

      {/* 8.5. AI Forensic Interpretation */}
      <AINarrativePanel analysisId={analysisId} />

      {/* 9. Management Questions */}
      <ManagementQuestionsPanel
        managementQuestions={assessment.management_questions}
        findings={assessment.forensic_findings}
      />

      {/* 10. Assessment Confidence */}
      <ConfidencePanel
        overall={assessment.overall}
        limitations={assessment.limitations}
        variablesAvailable={assessment.audit_trail?.variables_available || 0}
        variablesEvaluated={assessment.audit_trail?.variables_evaluated || 95}
      />

      {/* 11. Regulatory Audit Trail */}
      <AuditTrailPanel auditTrail={assessment.audit_trail} />

      {/* Drill-Down Dialog for Selected Pillar */}
      <PillarDetailDialog
        pillar={selectedPillar}
        open={Boolean(selectedPillar)}
        onClose={() => setSelectedPillar(null)}
      />
    </Box>
  )
}
