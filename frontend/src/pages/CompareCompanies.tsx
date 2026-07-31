import { Box, Stack, Typography } from '@mui/material'
import { useMemo, useState } from 'react'
import { companies, defaultCompanyIds, type CompanyComparison } from '../features/comparison/data'
import { ComparisonActions, CompanySelector, HeatmapTable, InsightsPanel, RadarComparison, RankingPanel, ScoreBarChart, SummaryTable } from '../features/comparison/components/ComparisonComponents'

export function CompareCompanies() {
  const [selected, setSelected] = useState<CompanyComparison[]>(() => companies.filter((company) => defaultCompanyIds.includes(company.id)))
  const selectedIds = useMemo(() => selected.map((company) => company.id), [selected])
  return <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1500, mx: 'auto' }}><Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" spacing={2} sx={{ mb: 3.5 }}><Box><Typography variant="h1">Compare companies</Typography><Typography color="text.secondary" sx={{ mt: .5 }}>Compare the forensic earnings quality of multiple companies using the EFS™ Framework.</Typography></Box><Box alignSelf={{ md: 'center' }}><ComparisonActions /></Box></Stack><Stack spacing={2}><CompanySelector selected={selected} onChange={setSelected} /><SummaryTable selected={selected} /><Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', xl: '1.15fr .85fr' }, gap: 2 }}><RadarComparison selected={selected} /><ScoreBarChart selected={selected} /></Box><HeatmapTable selected={selected} /><Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1.2fr' }, gap: 2 }}><RankingPanel selected={selected} /><InsightsPanel /></Box></Stack><Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 3 }}>Comparison uses the latest available dummy statements for {selectedIds.length} selected companies.</Typography></Box>
}
