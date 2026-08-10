import { useCallback, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Button, CircularProgress, Container, Paper, Typography, Alert } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import GetAppIcon from '@mui/icons-material/GetApp';

import { EFSService } from '../services/api/efsService';
import type { EFSResponse } from '../types/efs';

import { AssessmentHeader } from '../features/efs/components/AssessmentHeader';
import { AssessmentStatus } from '../features/efs/components/AssessmentStatus';
import { CalibrationNotice } from '../features/efs/components/CalibrationNotice';
import { ExecutiveSummary } from '../features/efs/components/ExecutiveSummary';
import { PillarsOverview } from '../features/efs/components/PillarsOverview';
import { PillarDetailDialog } from '../features/efs/components/PillarDetailDialog';
import { EstablishedModelsPanel } from '../features/efs/components/EstablishedModelsPanel';
import { ForensicFindingsPanel } from '../features/efs/components/ForensicFindingsPanel';
import { RedFlagsPanel } from '../features/efs/components/RedFlagsPanel';
import { ManagementQuestionsPanel } from '../features/efs/components/ManagementQuestionsPanel';
import { ConfidencePanel } from '../features/efs/components/ConfidencePanel';
import { AuditTrailPanel } from '../features/efs/components/AuditTrailPanel';

export function EFSReportPage() {
  const { analysisId = 'sample_analysis_001' } = useParams<{ analysisId: string }>();
  const navigate = useNavigate();

  const [assessment, setAssessment] = useState<EFSResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPillar, setSelectedPillar] = useState<any>(null);

  const fetchAssessment = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await EFSService.getAssessment(analysisId);
      setAssessment(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load EFS assessment.');
    } finally {
      setLoading(false);
    }
  }, [analysisId]);

  useEffect(() => {
    fetchAssessment();
  }, [fetchAssessment]);

  if (loading) {
    return (
      <Box sx={{ minHeight: '80vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', p: 4 }}>
        <CircularProgress size={48} sx={{ color: '#0f172a', mb: 2.5 }} />
        <Typography variant="h6" sx={{ fontWeight: 700, color: '#0f172a' }}>
          Generating EFS™ Report...
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Fetching assessment data for Analysis ID: {analysisId}
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Alert severity="error" action={<Button color="inherit" size="small" startIcon={<RefreshIcon />} onClick={fetchAssessment}>Retry</Button>} sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
            Unable to Load EFS™ Assessment
          </Typography>
          <Typography variant="body2">{error}</Typography>
        </Alert>
        <Button startIcon={<ArrowBackIcon />} variant="outlined" onClick={() => navigate('/')}>Return to Dashboard</Button>
      </Container>
    );
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
          <Button variant="contained" onClick={() => navigate('/analysis/new')}>Start New Assessment</Button>
        </Paper>
      </Container>
    );
  }

  // URL for server‑side PDF download
  const pdfUrl = `/api/v1/efs/${analysisId}/report`;

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1440, mx: 'auto' }}>
      {/* Header with download button */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>EFS™ Assessment Report Preview</Typography>
        <Button variant="contained" startIcon={<GetAppIcon />} href={pdfUrl} target="_blank" rel="noopener">
          Download PDF
        </Button>
      </Box>

      {/* 1. Assessment Header */}
      <AssessmentHeader
        companyName={assessment.company_name || 'Company'}
        ticker={assessment.ticker || ''}
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

      {/* 4. Executive Summary */}
      <ExecutiveSummary pillars={assessment.pillars} findings={assessment.forensic_findings} limitations={assessment.limitations} />

      {/* 5. Red Flags */}
      <RedFlagsPanel redFlags={assessment.red_flags} findings={assessment.forensic_findings} />

      {/* 6. Pillars Overview */}
      <PillarsOverview pillars={assessment.pillars} onSelectPillar={(p) => setSelectedPillar(p)} />

      {/* 7. Established Models */}
      <EstablishedModelsPanel models={assessment.established_models} />

      {/* 8. Forensic Findings */}
      <ForensicFindingsPanel findings={assessment.forensic_findings} />

      {/* 9. Management Questions */}
      <ManagementQuestionsPanel managementQuestions={assessment.management_questions} findings={assessment.forensic_findings} />

      {/* 10. Confidence Panel */}
      <ConfidencePanel overall={assessment.overall} limitations={assessment.limitations} variablesAvailable={assessment.audit_trail?.variables_available || 0} variablesEvaluated={assessment.audit_trail?.variables_evaluated || 95} />

      {/* 11. Audit Trail */}
      <AuditTrailPanel auditTrail={assessment.audit_trail} />

      {/* 12. Pillar Detail Dialog */}
      <PillarDetailDialog pillar={selectedPillar} open={Boolean(selectedPillar)} onClose={() => setSelectedPillar(null)} />
    </Box>
  );
}
