import { Box, Button, Stack, Typography } from '@mui/material'
import { useNavigate, useParams } from 'react-router-dom'
import { EmptyState, ErrorState, LoadingState } from '../components/feedback/FeedbackComponents'
export function LoadingPage() { return <UtilityPage><LoadingState label="Preparing your workspace" /></UtilityPage> }
export function EmptyPage() { const { variant = 'analysis' } = useParams(); const navigate = useNavigate(); return <UtilityPage><EmptyState variant={variant as 'history' | 'reports' | 'watchlist' | 'analysis'} onAction={() => navigate('/analysis/new')} /></UtilityPage> }
export function ErrorPage() { const { type = '404' } = useParams(); return <UtilityPage><ErrorState variant={type as '404' | '500' | 'network'} /></UtilityPage> }
export function DialogExamples() { const navigate = useNavigate(); return <UtilityPage><Box sx={{ maxWidth: 620, mx: 'auto' }}><Typography variant="h2">Reusable feedback patterns</Typography><Typography color="text.secondary" sx={{ mt: 1, mb: 3 }}>Dialog patterns are available to feature pages as reusable components.</Typography><Stack direction="row" spacing={1}><Button variant="contained" onClick={() => navigate('/reports')}>View report examples</Button><Button variant="outlined" onClick={() => navigate('/')}>Go home</Button></Stack></Box></UtilityPage> }
function UtilityPage({ children }: { children: React.ReactNode }) { return <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1000, mx: 'auto' }}>{children}</Box> }
