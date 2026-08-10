import { Box, Card, Chip, Grid, Paper, Stack, Typography } from '@mui/material'
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer'
import type { ForensicFinding } from '../../../types/efs'

interface ManagementQuestionsPanelProps {
  managementQuestions?: string[]
  findings: ForensicFinding[]
}

export function ManagementQuestionsPanel({ managementQuestions = [], findings = [] }: ManagementQuestionsPanelProps) {
  // Group questions by pillar
  const groupedQuestions: Record<string, string[]> = {}

  findings.forEach((f) => {
    if (f.triggered && f.question_for_management) {
      const pName = f.pillar || 'General Accounting & Disclosure'
      if (!groupedQuestions[pName]) {
        groupedQuestions[pName] = []
      }
      if (!groupedQuestions[pName].includes(f.question_for_management)) {
        groupedQuestions[pName].push(f.question_for_management)
      }
    }
  })

  const groupKeys = Object.keys(groupedQuestions)

  return (
    <Box sx={{ mb: 4 }}>
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
        <QuestionAnswerIcon sx={{ color: '#4f46e5' }} />
        <Typography variant="h6" sx={{ fontWeight: 700, color: '#0f172a' }}>
          Management Inquiry Questions ({managementQuestions.length || groupKeys.reduce((a, b) => a + groupedQuestions[b].length, 0)})
        </Typography>
      </Stack>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Rulebook-generated targeted inquiries for management and audit committee discussion based on triggered forensic signals.
      </Typography>

      {groupKeys.length > 0 ? (
        <Grid container spacing={2}>
          {groupKeys.map((pName) => (
            <Grid size={{ xs: 12, md: 6 }} key={pName}>
              <Card elevation={0} sx={{ p: 2.5, borderRadius: 2, border: '1px solid #cbd5e1', bgcolor: '#ffffff', height: '100%' }}>
                <Chip label={pName} size="small" sx={{ bgcolor: '#e0e7ff', color: '#4338ca', fontWeight: 800, mb: 1.5 }} />
                <Stack spacing={1.5}>
                  {groupedQuestions[pName].map((q, idx) => (
                    <Box key={idx} sx={{ p: 1.5, bgcolor: '#f8fafc', borderRadius: 1.5, border: '1px solid #e2e8f0' }}>
                      <Typography variant="body2" sx={{ fontWeight: 600, color: '#1e293b' }}>
                        {idx + 1}. "{q}"
                      </Typography>
                    </Box>
                  ))}
                </Stack>
              </Card>
            </Grid>
          ))}
        </Grid>
      ) : managementQuestions.length > 0 ? (
        <Card elevation={0} sx={{ p: 2.5, borderRadius: 2, border: '1px solid #cbd5e1', bgcolor: '#ffffff' }}>
          <Stack spacing={1.5}>
            {managementQuestions.map((q, idx) => (
              <Box key={idx} sx={{ p: 1.5, bgcolor: '#f8fafc', borderRadius: 1.5, border: '1px solid #e2e8f0' }}>
                <Typography variant="body2" sx={{ fontWeight: 600, color: '#1e293b' }}>
                  {idx + 1}. "{q}"
                </Typography>
              </Box>
            ))}
          </Stack>
        </Card>
      ) : (
        <Paper elevation={0} sx={{ p: 3, textAlign: 'center', bgcolor: '#ffffff', border: '1px solid #cbd5e1', borderRadius: 2 }}>
          <Typography variant="body2" color="text.secondary">
            No management questions triggered for the current evidence state.
          </Typography>
        </Paper>
      )}
    </Box>
  )
}
