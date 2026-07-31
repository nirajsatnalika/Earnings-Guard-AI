import { CheckCircleOutline, FileDownloadOutlined } from '@mui/icons-material'
import { Box, Button, Card, Chip, Stack, Tab, Tabs, Typography } from '@mui/material'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AiReportTab, KpiCard, OverviewTab, PillarTab, RatiosTab, RedFlagsTab, StatementsTab } from '../features/results/components/ResultsComponents'
import { kpis } from '../features/results/data'

const tabs = ['Overview', 'Pillar Scores', 'Financial Statements', 'Ratios', 'Red Flags', 'AI Report']

export function Results() {
  const [tab, setTab] = useState(0)
  const navigate = useNavigate()
  const content = [<OverviewTab />, <PillarTab />, <StatementsTab />, <RatiosTab />, <RedFlagsTab />, <AiReportTab />][tab]
  return <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1440, mx: 'auto' }}><Stack direction={{ xs: 'column', lg: 'row' }} justifyContent="space-between" spacing={2} sx={{ mb: 3 }}><Box><Stack direction="row" spacing={1} alignItems="center"><Typography variant="h1">Forensic analysis results</Typography><Chip label="Completed" color="success" size="small" icon={<CheckCircleOutline />} /></Stack><Stack direction={{ xs: 'column', sm: 'row' }} spacing={{ xs: .5, sm: 3 }} sx={{ mt: 1 }}><Typography variant="body2" color="text.secondary"><strong>Infosys Ltd.</strong> · INFY</Typography><Typography variant="body2" color="text.secondary">FY2025</Typography><Typography variant="body2" color="text.secondary">Analysis time: 12.8 seconds</Typography></Stack></Box><Stack direction="row" spacing={1} alignSelf={{ lg: 'center' }}><Button variant="outlined" onClick={() => navigate('/analysis/new')}>New analysis</Button><Button variant="contained" startIcon={<FileDownloadOutlined />}>Download report</Button></Stack></Stack><Box sx={{ display: 'grid', gridTemplateColumns: { xs: 'repeat(2, 1fr)', sm: 'repeat(3, 1fr)', lg: 'repeat(6, 1fr)' }, gap: 1.5, mb: 3 }}>{kpis.map((item) => <KpiCard key={item.label} item={item} />)}</Box><Card sx={{ mb: 3, overflowX: 'auto' }}><Tabs value={tab} onChange={(_, value) => setTab(value)} variant="scrollable" scrollButtons="auto" sx={{ minHeight: 54, '& .MuiTab-root': { minHeight: 54, fontSize: '.78rem', fontWeight: 700 } }}>{tabs.map((label) => <Tab key={label} label={label} />)}</Tabs></Card>{content}</Box>
}
