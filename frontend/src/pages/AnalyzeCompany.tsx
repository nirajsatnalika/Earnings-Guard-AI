import { useEffect, useMemo, useRef, useState } from 'react'
import { CheckCircleOutline, ChevronLeft, ChevronRight, ErrorOutline, InfoOutlined, PlayArrow, WarningAmberOutlined } from '@mui/icons-material'
import { Alert, Box, Button, Card, CardContent, Chip, FormControl, InputLabel, LinearProgress, MenuItem, Select, Stack, Step, StepLabel, Stepper, TextField, Typography } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { analysisChecklist, countries, financialYears, industries, initialMappings } from '../features/analysis/data'
import { MappingTable } from '../features/analysis/components/MappingTable'
import { UploadCard } from '../features/analysis/components/UploadCard'
import type { AnalysisStep, CompanyDetails, FieldMapping, UploadedStatement } from '../features/analysis/types'
import { UploadService, type UploadProgress } from '../services/api'
import { useToast } from '../services/feedback'

const steps = ['Company Information', 'Upload Statements', 'Field Mapping', 'Validation', 'Analysis Running']
const initialCompany: CompanyDetails = { companyName: '', stockSymbol: '', industry: '', country: '', financialYear: '' }
const statementTypes: UploadedStatement['type'][] = ['Balance Sheet', 'Profit & Loss Statement', 'Cash Flow Statement']

export function AnalyzeCompany() {
  const navigate = useNavigate()
  const toast = useToast()
  const [activeStep, setActiveStep] = useState<AnalysisStep>(0)
  const [company, setCompany] = useState(initialCompany)
  const [statements, setStatements] = useState<UploadedStatement[]>(statementTypes.map((type) => ({ type, file: null, progress: 0 })))
  const [mappings, setMappings] = useState<FieldMapping[]>(initialMappings)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [analysisId, setAnalysisId] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => { if (activeStep !== 4) return; const timer = window.setInterval(() => setAnalysisProgress((value) => Math.min(value + 2, 100)), 100); return () => window.clearInterval(timer) }, [activeStep])
  useEffect(() => { if (analysisProgress === 100) { const timer = window.setTimeout(() => navigate('/results'), 700); return () => window.clearTimeout(timer) } }, [analysisProgress, navigate])
  useEffect(() => () => abortRef.current?.abort(), [])

  const updateCompany = (key: keyof CompanyDetails, value: string) => setCompany((current) => ({ ...current, [key]: value }))
  const updateFile = (index: number, file: File | null) => { setStatements((current) => current.map((statement, statementIndex) => statementIndex === index ? { ...statement, file, progress: file ? 0 : 0 } : statement)) }
  const updateMapping = (index: number, value: string) => setMappings((current) => current.map((mapping, mappingIndex) => mappingIndex === index ? { ...mapping, standardField: value } : mapping))
  const canContinue = activeStep === 0 ? Boolean(company.companyName && company.stockSymbol && company.industry && company.country && company.financialYear) : activeStep === 1 ? statements.every(({ file }) => file) && !uploading : true
  const missingFields = useMemo(() => ['Revenue', 'PAT', 'CFO'].filter((field) => !mappings.some((mapping) => mapping.standardField === field)), [mappings])

  const next = () => setActiveStep((step) => Math.min(step + 1, 4) as AnalysisStep)
  const back = () => setActiveStep((step) => Math.max(step - 1, 0) as AnalysisStep)

  const handleUpload = async () => {
    const filesToUpload = statements.filter((statement) => statement.file).map((statement) => ({ statementType: statement.type, file: statement.file as File }))
    if (filesToUpload.length === 0) return
    setUploading(true)
    abortRef.current = new AbortController()
    try {
      const result = await UploadService.uploadStatements(
        filesToUpload,
        (progress: UploadProgress) => {
          setStatements((current) => current.map((statement) => statement.type === progress.statementType ? { ...statement, progress: progress.progress } : statement))
        },
        abortRef.current.signal,
      )
      setAnalysisId(result.analysisId)
      toast.notifySuccess(`Uploaded ${result.uploadedFiles.length} statement${result.uploadedFiles.length === 1 ? '' : 's'} successfully.`)
      setActiveStep(2)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Upload failed. Please try again.'
      toast.notifyError(message)
      setStatements((current) => current.map((statement) => ({ ...statement, progress: 0 })))
    } finally {
      setUploading(false)
      abortRef.current = null
    }
  }

  return <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1180, mx: 'auto' }}><Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" spacing={2} sx={{ mb: 3.5 }}><Box><Typography variant="h1">Analyze company</Typography><Typography color="text.secondary" sx={{ mt: .5 }}>Build an evidence-backed earnings profile in five simple steps.</Typography></Box><Chip label="New analysis" color="primary" variant="outlined" sx={{ alignSelf: { md: 'center' } }} /></Stack><Card sx={{ mb: 3, overflowX: 'auto' }}><Stepper activeStep={activeStep} sx={{ p: { xs: 2, md: 3 }, minWidth: 720 }}>{steps.map((step) => <Step key={step}><StepLabel>{step}</StepLabel></Step>)}</Stepper></Card>{activeStep === 0 && <CompanyInformation company={company} updateCompany={updateCompany} />}{activeStep === 1 && <UploadStatements statements={statements} updateFile={updateFile} uploading={uploading} />}{activeStep === 2 && <MappingTable mappings={mappings} onChange={updateMapping} onAutoMap={() => setMappings(initialMappings)} />}{activeStep === 3 && <Validation missingFields={missingFields} analysisId={analysisId} />}{activeStep === 4 && <AnalysisRunning progress={analysisProgress} />}{activeStep < 4 && <Stack direction="row" justifyContent="space-between" sx={{ mt: 3 }}><Button onClick={activeStep === 0 ? () => navigate('/') : back}>{activeStep === 0 ? 'Cancel' : 'Back'}</Button>{activeStep === 1 ? <Button variant="contained" endIcon={<ChevronRight />} disabled={!canContinue} onClick={handleUpload}>{uploading ? 'Uploading…' : 'Upload & continue'}</Button> : <Button variant="contained" endIcon={activeStep === 3 ? <PlayArrow /> : <ChevronRight />} disabled={!canContinue} onClick={next}>{activeStep === 3 ? 'Run analysis' : 'Next'}</Button>}</Stack>}{activeStep === 4 && <Button startIcon={<ChevronLeft />} onClick={back} sx={{ mt: 2 }}>Back to validation</Button>}</Box>
}

function CompanyInformation({ company, updateCompany }: { company: CompanyDetails; updateCompany: (key: keyof CompanyDetails, value: string) => void }) {
  const field = (key: keyof CompanyDetails, label: string, placeholder: string) => <TextField label={label} placeholder={placeholder} value={company[key]} onChange={(event) => updateCompany(key, event.target.value)} fullWidth required />
  const select = (key: keyof CompanyDetails, label: string, values: string[]) => <FormControl fullWidth required><InputLabel>{label}</InputLabel><Select label={label} value={company[key]} onChange={(event) => updateCompany(key, event.target.value)}>{values.map((value) => <MenuItem key={value} value={value}>{value}</MenuItem>)}</Select></FormControl>
  return <Card><CardContent sx={{ p: { xs: 2, md: 4 } }}><Box sx={{ maxWidth: 760 }}><Typography variant="h2">Tell us about the company</Typography><Typography color="text.secondary" sx={{ mt: .75, mb: 3.5 }}>We’ll use this information to prepare the right financial benchmarks and analysis context.</Typography><Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2.5 }}>{field('companyName', 'Company name', 'e.g. Acme Corporation')}{field('stockSymbol', 'Stock symbol', 'e.g. ACME')}{select('industry', 'Industry', industries)}{select('country', 'Country', countries)}{select('financialYear', 'Financial year', financialYears)}</Box></Box></CardContent></Card>
}

function UploadStatements({ statements, updateFile, uploading }: { statements: UploadedStatement[]; updateFile: (index: number, file: File | null) => void; uploading: boolean }) {
  return <Box><Typography variant="h2">Upload financial statements</Typography><Typography color="text.secondary" sx={{ mt: .75, mb: 2.5 }}>Upload the latest annual statements. We accept Excel and CSV files only.</Typography><Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' }, gap: 2 }}>{statements.map((statement, index) => <UploadCard key={statement.type} statement={statement} onFileChange={(file) => updateFile(index, file)} disabled={uploading} />)}</Box><Alert severity="info" icon={<InfoOutlined />} sx={{ mt: 2 }}>For best results, upload statements from the same financial year.</Alert></Box>
}

function Validation({ missingFields, analysisId }: { missingFields: string[]; analysisId: string | null }) {
  const checks = [{ label: 'Revenue Found', ok: !missingFields.includes('Revenue') }, { label: 'PAT Found', ok: !missingFields.includes('PAT') }, { label: 'CFO Found', ok: !missingFields.includes('CFO') }, { label: 'Inventory Missing', ok: false }, { label: 'Depreciation Missing', ok: false }]
  return <Box><Typography variant="h2">Validation</Typography><Typography color="text.secondary" sx={{ mt: .75, mb: 2.5 }}>Review the data quality checks before running the analysis.</Typography>{analysisId && <Alert severity="success" icon={<CheckCircleOutline />} sx={{ mb: 2 }}>Statements uploaded. Analysis ID: <strong>{analysisId}</strong></Alert>}<Card><CardContent sx={{ p: { xs: 2, md: 3 } }}><Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ sm: 'center' }} sx={{ mb: 3 }}><Box sx={{ flex: 1 }}><Typography variant="h3">Validation summary</Typography><Typography variant="body2" color="text.secondary" sx={{ mt: .5 }}>18 of 20 recommended fields reviewed</Typography></Box><Typography variant="h2" color="warning.main">90%</Typography></Stack><LinearProgress variant="determinate" value={90} color="warning" sx={{ height: 7, borderRadius: 4, mb: 3 }} /><Stack spacing={1.25}>{checks.map((check) => <Stack direction="row" alignItems="center" spacing={1.25} key={check.label} sx={{ p: 1.25, bgcolor: check.ok ? 'rgba(15,159,114,.06)' : 'rgba(217,139,16,.07)', borderRadius: 1.5 }}>{check.ok ? <CheckCircleOutline color="success" fontSize="small" /> : <WarningAmberOutlined color="warning" fontSize="small" />}<Typography variant="body2" fontWeight={650}>{check.label}</Typography><Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>{check.ok ? 'Successfully detected' : 'Warning'}</Typography></Stack>)}</Stack></CardContent></Card><Alert severity="warning" icon={<ErrorOutline />} sx={{ mt: 2 }}>Some optional fields are missing. You can still run the analysis, but the confidence score may be lower.</Alert></Box>
}

function AnalysisRunning({ progress }: { progress: number }) {
  const completed = Math.floor((progress / 100) * analysisChecklist.length)
  return <Card><CardContent sx={{ p: { xs: 3, md: 6 }, textAlign: 'center' }}><Box sx={{ maxWidth: 560, mx: 'auto' }}><Box sx={{ width: 64, height: 64, borderRadius: '50%', border: '3px solid', borderColor: 'primary.main', display: 'grid', placeItems: 'center', mx: 'auto', mb: 2, animation: 'pulse 1.8s ease-in-out infinite', '@keyframes pulse': { '50%': { transform: 'scale(1.06)', opacity: .7 } } }}><PlayArrow color="primary" /></Box><Typography variant="h2">Analyzing your company</Typography><Typography color="text.secondary" sx={{ mt: .75 }}>EarningsGuard™ AI is turning your statements into actionable intelligence.</Typography><Stack direction="row" alignItems="center" spacing={2} sx={{ mt: 4 }}><LinearProgress variant="determinate" value={progress} sx={{ flex: 1, height: 8, borderRadius: 4 }} /><Typography variant="body2" fontWeight={750} sx={{ minWidth: 40, textAlign: 'right' }}>{progress}%</Typography></Stack><Stack spacing={1.25} sx={{ mt: 4, textAlign: 'left' }}>{analysisChecklist.map((item, index) => <Stack direction="row" alignItems="center" spacing={1.25} key={item} sx={{ color: index < completed ? 'success.main' : 'text.secondary' }}>{index < completed ? <CheckCircleOutline fontSize="small" /> : <Box sx={{ width: 18, height: 18, border: '1px solid', borderColor: 'divider', borderRadius: '50%' }} />}<Typography variant="body2" fontWeight={index < completed ? 700 : 500}>{item}</Typography>{index < completed && <Chip label="Complete" size="small" color="success" variant="outlined" sx={{ ml: 'auto' }} />}</Stack>)}</Stack></Box></CardContent></Card>
}
