import { ThemeProvider } from '@mui/material/styles'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/layout/AppShell'
import { Dashboard } from './pages/Dashboard'
import { AnalyzeCompany } from './pages/AnalyzeCompany'
import { Results } from './pages/Results'
import { CompareCompanies } from './pages/CompareCompanies'
import { PlaceholderPage } from './pages/PlaceholderPage'
import { History } from './pages/History'
import { Watchlist } from './pages/Watchlist'
import { Reports } from './pages/Reports'
import { Settings } from './pages/Settings'
import { Login } from './pages/Login'
import { DialogExamples, EmptyPage, ErrorPage, LoadingPage } from './pages/UtilityPages'
import { theme } from './theme'
import './App.css'

function App() {
  return <ThemeProvider theme={theme}><BrowserRouter><Routes><Route path="/login" element={<Login />} /><Route element={<AppShell />}><Route path="/" element={<Dashboard />} /><Route path="/analysis/new" element={<AnalyzeCompany />} /><Route path="/results" element={<Results />} /><Route path="/results/pillar/:pillarId" element={<PlaceholderPage />} /><Route path="/history" element={<History />} /><Route path="/compare" element={<CompareCompanies />} /><Route path="/watchlist" element={<Watchlist />} /><Route path="/reports" element={<Reports />} /><Route path="/alerts" element={<PlaceholderPage />} /><Route path="/settings" element={<Settings />} /><Route path="/loading" element={<LoadingPage />} /><Route path="/empty/:variant" element={<EmptyPage />} /><Route path="/error/:type" element={<ErrorPage />} /><Route path="/dialog-examples" element={<DialogExamples />} /><Route path="*" element={<Navigate to="/" replace />} /></Route></Routes></BrowserRouter></ThemeProvider>
}

export default App
