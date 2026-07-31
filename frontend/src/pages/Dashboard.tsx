import type { ReactNode } from 'react'
import { ArrowDownward, ArrowUpward, ChevronRight, MoreHoriz, ShieldOutlined, TrendingUp } from '@mui/icons-material'
import { Box, Button, Card, CardContent, Chip, Grid, IconButton, LinearProgress, Stack, Typography } from '@mui/material'
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

const chartData = [
  { month: 'Feb', score: 64 }, { month: 'Mar', score: 68 }, { month: 'Apr', score: 66 },
  { month: 'May', score: 73 }, { month: 'Jun', score: 71 }, { month: 'Jul', score: 82 },
]
const companies = [
  { ticker: 'NVDA', name: 'NVIDIA Corporation', score: 92, change: '+4.8%', status: 'Low risk', color: 'success' as const },
  { ticker: 'MSFT', name: 'Microsoft Corporation', score: 87, change: '+2.1%', status: 'Low risk', color: 'success' as const },
  { ticker: 'TSLA', name: 'Tesla, Inc.', score: 61, change: '-3.6%', status: 'Watch', color: 'warning' as const },
  { ticker: 'META', name: 'Meta Platforms, Inc.', score: 78, change: '+1.4%', status: 'Moderate', color: 'info' as const },
]

function MetricCard({ label, value, detail, positive = true, icon }: { label: string; value: string; detail: string; positive?: boolean; icon: ReactNode }) {
  return <Card sx={{ height: '100%' }}><CardContent sx={{ p: 2.5, '&:last-child': { pb: 2.5 } }}><Stack direction="row" justifyContent="space-between" alignItems="flex-start"><Typography variant="body2" color="text.secondary">{label}</Typography><Box sx={{ color: 'primary.main', bgcolor: 'rgba(99,91,255,.1)', p: .75, borderRadius: 1.5, display: 'flex' }}>{icon}</Box></Stack><Typography sx={{ mt: 2, fontSize: '1.75rem', fontWeight: 750, letterSpacing: '-.04em' }}>{value}</Typography><Stack direction="row" spacing={.5} alignItems="center" sx={{ mt: .75 }}><Box sx={{ color: positive ? 'success.main' : 'error.main', display: 'flex' }}>{positive ? <ArrowUpward sx={{ fontSize: 14 }} /> : <ArrowDownward sx={{ fontSize: 14 }} />}</Box><Typography variant="caption" color={positive ? 'success.main' : 'error.main'}>{detail}</Typography><Typography variant="caption" color="text.secondary">vs last month</Typography></Stack></CardContent></Card>
}

export function Dashboard() {
  return <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1500, mx: 'auto' }}>
    <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ sm: 'center' }} spacing={2} sx={{ mb: 3.5 }}>
      <Box><Typography variant="h1">Good morning, Alex</Typography><Typography color="text.secondary" sx={{ mt: .5 }}>Here is your portfolio intelligence for Tuesday, July 22, 2026.</Typography></Box>
      <Button variant="contained" startIcon={<ShieldOutlined />} href="/analysis/new">Run new analysis</Button>
    </Stack>

    <Grid container spacing={2} sx={{ mb: 2 }}>
      <Grid size={{ xs: 12, sm: 6, lg: 3 }}><MetricCard label="Portfolio health" value="84 / 100" detail="6.2%" icon={<ShieldOutlined fontSize="small" />} /></Grid>
      <Grid size={{ xs: 12, sm: 6, lg: 3 }}><MetricCard label="Earnings reviewed" value="128" detail="12.5%" icon={<TrendingUp fontSize="small" />} /></Grid>
      <Grid size={{ xs: 12, sm: 6, lg: 3 }}><MetricCard label="Active watchlist" value="24" detail="3.1%" icon={<ShieldOutlined fontSize="small" />} /></Grid>
      <Grid size={{ xs: 12, sm: 6, lg: 3 }}><MetricCard label="Risk alerts" value="03" detail="1 new" positive={false} icon={<ShieldOutlined fontSize="small" />} /></Grid>
    </Grid>

    <Grid container spacing={2}>
      <Grid size={{ xs: 12, lg: 8 }}><Card sx={{ height: '100%' }}><CardContent sx={{ p: 2.5 }}><Stack direction="row" justifyContent="space-between" alignItems="flex-start"><Box><Typography variant="h3">Portfolio health score</Typography><Typography variant="body2" color="text.secondary" sx={{ mt: .5 }}>Weighted confidence across your monitored companies</Typography></Box><Chip label="Last 6 months" size="small" variant="outlined" /></Stack><Box sx={{ height: 260, mt: 2 }}><ResponsiveContainer width="100%" height="100%"><AreaChart data={chartData} margin={{ top: 15, right: 8, left: -22, bottom: 0 }}><defs><linearGradient id="scoreFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#635bff" stopOpacity={.22} /><stop offset="100%" stopColor="#635bff" stopOpacity={0} /></linearGradient></defs><XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#8b95a7', fontSize: 11 }} /><YAxis domain={[40, 100]} axisLine={false} tickLine={false} tick={{ fill: '#8b95a7', fontSize: 11 }} /><Tooltip contentStyle={{ border: '1px solid #e7eaf0', borderRadius: 8, boxShadow: '0 4px 12px rgba(0,0,0,.08)' }} /><Area type="monotone" dataKey="score" stroke="#635bff" strokeWidth={2.5} fill="url(#scoreFill)" /></AreaChart></ResponsiveContainer></Box></CardContent></Card></Grid>
      <Grid size={{ xs: 12, lg: 4 }}><Card sx={{ height: '100%' }}><CardContent sx={{ p: 2.5 }}><Stack direction="row" justifyContent="space-between" alignItems="center"><Box><Typography variant="h3">Upcoming earnings</Typography><Typography variant="body2" color="text.secondary" sx={{ mt: .5 }}>Next 7 days</Typography></Box><IconButton size="small"><MoreHoriz /></IconButton></Stack><Stack spacing={2.25} sx={{ mt: 3 }}>{[['GOOGL', 'Jul 23', 'After close'], ['AMZN', 'Jul 24', 'After close'], ['AAPL', 'Jul 25', 'After close'], ['INTC', 'Jul 28', 'After close']].map(([ticker, date, time]) => <Stack key={ticker} direction="row" alignItems="center" spacing={1.5}><Box sx={{ width: 34, height: 34, borderRadius: 1.5, display: 'grid', placeItems: 'center', bgcolor: '#f0f1ff', color: 'primary.main', fontSize: 10, fontWeight: 800 }}>{ticker.slice(0, 2)}</Box><Box sx={{ flex: 1 }}><Typography fontSize=".8rem" fontWeight={700}>{ticker}</Typography><Typography variant="caption" color="text.secondary">{time}</Typography></Box><Typography variant="body2" fontWeight={650}>{date}</Typography></Stack>)}</Stack><Button fullWidth endIcon={<ChevronRight />} sx={{ mt: 2.5, justifyContent: 'space-between' }}>View earnings calendar</Button></CardContent></Card></Grid>
      <Grid size={{ xs: 12 }}><Card><CardContent sx={{ p: 2.5 }}><Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}><Box><Typography variant="h3">Watchlist overview</Typography><Typography variant="body2" color="text.secondary" sx={{ mt: .5 }}>Real-time risk signals for your highest-priority companies</Typography></Box><Button endIcon={<ChevronRight />}>View all</Button></Stack><Box sx={{ overflowX: 'auto' }}><Box sx={{ minWidth: 620 }}><Stack direction="row" sx={{ px: 1.5, pb: 1, color: 'text.secondary' }}><Typography variant="caption" sx={{ width: '34%' }}>COMPANY</Typography><Typography variant="caption" sx={{ width: '22%' }}>GUARD SCORE</Typography><Typography variant="caption" sx={{ width: '22%' }}>STOCK MOVE</Typography><Typography variant="caption">STATUS</Typography></Stack>{companies.map((company) => <Stack key={company.ticker} direction="row" alignItems="center" sx={{ px: 1.5, py: 1.5, borderTop: 1, borderColor: 'divider' }}><Box sx={{ width: '34%' }}><Typography fontWeight={750} fontSize=".82rem">{company.ticker}</Typography><Typography variant="caption" color="text.secondary" fontWeight={500}>{company.name}</Typography></Box><Box sx={{ width: '22%', pr: 3 }}><Stack direction="row" alignItems="center" spacing={1}><Typography fontWeight={750} fontSize=".82rem">{company.score}</Typography><LinearProgress variant="determinate" value={company.score} sx={{ flex: 1, height: 5, borderRadius: 4, bgcolor: '#eceef5', '& .MuiLinearProgress-bar': { borderRadius: 4, bgcolor: company.score > 80 ? 'success.main' : 'warning.main' } }} /></Stack></Box><Typography sx={{ width: '22%', color: company.change.startsWith('+') ? 'success.main' : 'error.main', fontSize: '.8rem', fontWeight: 700 }}>{company.change}</Typography><Chip label={company.status} color={company.color} size="small" variant="outlined" /></Stack>)}</Box></Box></CardContent></Card></Grid>
    </Grid>
  </Box>
}
