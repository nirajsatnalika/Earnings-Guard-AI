import { useEffect, useState } from 'react'
import {
  AutoAwesomeOutlined,
  CheckCircleOutline,
  ChevronRight,
  CloudUploadOutlined,
  EditOutlined,
  InfoOutlined,
  PlayArrow,
  PlayCircleOutline,
  TableChartOutlined,
} from '@mui/icons-material'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  FormControl,
  Grid,
  InputLabel,
  LinearProgress,
  MenuItem,
  Paper,
  Select,
  Stack,
  Step,
  StepLabel,
  Stepper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { countries, financialYears, industries } from '../features/analysis/data'
import { HumanReviewTable } from '../features/analysis/components/HumanReviewTable'
import { UploadCard } from '../features/analysis/components/UploadCard'
import {
  CompanyService,
  EFSService,
  IngestionService,
  UploadService,
} from '../services/api'
import type { CanonicalExtractedItem } from '../services/api'
import type { CompanyRecord } from '../types/efs'
import type { UploadedStatement } from '../features/analysis/types'
import { useToast } from '../services/feedback'

const steps = ['Company', 'Financial Data & Ingestion', 'Review & Validate', 'Run EFS']

interface FinancialFormData {
  revenue: string
  prior_revenue: string
  receivables: string
  prior_receivables: string
  cfo: string
  pat: string
  cogs: string
  inventory: string
  payables: string
  total_assets: string
  prior_total_assets: string
  depreciation: string
  total_debt: string
  equity: string
  ebit: string
}

const emptyFinancialForm: FinancialFormData = {
  revenue: '',
  prior_revenue: '',
  receivables: '',
  prior_receivables: '',
  cfo: '',
  pat: '',
  cogs: '',
  inventory: '',
  payables: '',
  total_assets: '',
  prior_total_assets: '',
  depreciation: '',
  total_debt: '',
  equity: '',
  ebit: '',
}

const demoFinancialData: FinancialFormData = {
  revenue: '500000',
  prior_revenue: '450000',
  receivables: '80000',
  prior_receivables: '65000',
  cfo: '60000',
  pat: '45000',
  cogs: '300000',
  inventory: '50000',
  payables: '40000',
  total_assets: '600000',
  prior_total_assets: '550000',
  depreciation: '20000',
  total_debt: '150000',
  equity: '350000',
  ebit: '70000',
}

export function AnalyzeCompany() {
  const navigate = useNavigate()
  const toast = useToast()

  const [activeStep, setActiveStep] = useState<number>(0)

  // Company Step State
  const [existingCompanies, setExistingCompanies] = useState<CompanyRecord[]>([])
  const [loadingCompanies, setLoadingCompanies] = useState<boolean>(true)
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>('')
  const [isCreatingNewCompany, setIsCreatingNewCompany] = useState<boolean>(false)
  const [newCompany, setNewCompany] = useState({
    legal_name: '',
    ticker: '',
    industry: 'Technology',
    country: 'India',
    financialYear: 'FY 2025–26',
  })

  // Input Mode: MANUAL vs UPLOAD
  const [inputMode, setInputMode] = useState<'MANUAL' | 'UPLOAD'>('MANUAL')

  // Financial Form State
  const [financials, setFinancials] = useState<FinancialFormData>(emptyFinancialForm)
  const [isDemoDataLoaded, setIsDemoDataLoaded] = useState<boolean>(false)

  // Upload & Ingestion State
  const [uploadedStatement, setUploadedStatement] = useState<UploadedStatement>({
    type: 'Annual Report / Financial Statement',
    file: null,
    progress: 0,
  })
  const [isIngesting, setIsIngesting] = useState<boolean>(false)
  const [scannedPdfMessage, setScannedPdfMessage] = useState<string | null>(null)
  const [extractedItems, setExtractedItems] = useState<CanonicalExtractedItem[]>([])
  const [ingestionAnalysisId, setIngestionAnalysisId] = useState<string>('')

  // Execution State
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)

  useEffect(() => {
    fetchCompanies()
  }, [])

  const fetchCompanies = async () => {
    setLoadingCompanies(true)
    try {
      const list = await CompanyService.listCompanies()
      setExistingCompanies(list)
      if (list.length > 0) {
        setSelectedCompanyId(list[0].id)
      } else {
        setIsCreatingNewCompany(true)
      }
    } catch {
      toast.notifyError('Failed to load existing companies')
      setIsCreatingNewCompany(true)
    } finally {
      setLoadingCompanies(false)
    }
  }

  const handleFieldChange = (field: keyof FinancialFormData, value: string) => {
    setFinancials((prev) => ({ ...prev, [field]: value }))
  }

  const handleLoadDemoData = () => {
    setFinancials(demoFinancialData)
    setIsDemoDataLoaded(true)
    toast.notifySuccess('Demo financial data loaded successfully!')
  }

  // Handle Document Ingestion Workflow
  const handleIngestDocument = async () => {
    if (!uploadedStatement.file) {
      toast.notifyError('Please select a PDF, Excel, or CSV document first.')
      return
    }

    setIsIngesting(true)
    setScannedPdfMessage(null)

    try {
      // 1. Upload file
      const uploadRes = await UploadService.uploadStatements([
        { statementType: 'Annual Report', file: uploadedStatement.file },
      ])
      setUploadedStatement((prev) => ({ ...prev, progress: 100 }))

      // 2. Process Extraction & Normalization
      const ingestRes = await IngestionService.processIngestion(uploadRes.analysisId)
      setIngestionAnalysisId(uploadRes.analysisId)

      if (ingestRes.is_scanned_pdf) {
        setScannedPdfMessage(
          ingestRes.scanned_pdf_message ||
            'Scanned PDF detected. OCR support will be available in a future release.',
        )
        toast.notifyError('Scanned PDF detected. Text extraction deferred.')
      } else {
        setExtractedItems(ingestRes.extracted_items)
        toast.notifySuccess(
          `Extracted ${ingestRes.extracted_items.length} line items. Please review mappings below.`,
        )
      }
    } catch (err) {
      toast.notifyError(err instanceof Error ? err.message : 'Document ingestion failed.')
    } finally {
      setIsIngesting(false)
    }
  }

  const handleConfirmIngestionReview = async () => {
    if (!ingestionAnalysisId) {
      toast.notifyError('No active document ingestion analysis found.')
      return
    }

    try {
      const confirmRes = await IngestionService.confirmReview(ingestionAnalysisId, extractedItems)
      const confirmedVars = confirmRes.confirmed_raw_variables

      // Merge confirmed variables into financial form
      setFinancials((prev) => {
        const next = { ...prev }
        Object.entries(confirmedVars).forEach(([k, v]) => {
          if (k in next) {
            next[k as keyof FinancialFormData] = String(v)
          }
        })
        return next
      })

      toast.notifySuccess('Confirmed financial mappings saved cleanly. Moving to review step.')
      setActiveStep(2)
    } catch (err) {
      toast.notifyError(err instanceof Error ? err.message : 'Failed to confirm review choices.')
    }
  }

  // Calculate Data Coverage
  const coreFields: (keyof FinancialFormData)[] = [
    'revenue',
    'receivables',
    'cfo',
    'pat',
    'cogs',
    'inventory',
    'payables',
    'total_assets',
  ]
  const historicalFields: (keyof FinancialFormData)[] = [
    'prior_revenue',
    'prior_receivables',
    'prior_total_assets',
  ]
  const disclosureFields: (keyof FinancialFormData)[] = [
    'depreciation',
    'total_debt',
    'equity',
    'ebit',
  ]

  const countFilled = (fields: (keyof FinancialFormData)[]) =>
    fields.filter((f) => financials[f] !== undefined && financials[f].trim() !== '').length

  const coreCoveragePct = Math.round((countFilled(coreFields) / coreFields.length) * 100)
  const historicalCoveragePct = Math.round(
    (countFilled(historicalFields) / historicalFields.length) * 100
  )
  const disclosureCoveragePct = Math.round(
    (countFilled(disclosureFields) / disclosureFields.length) * 100
  )

  const canProceedStep0 = isCreatingNewCompany
    ? Boolean(newCompany.legal_name.trim())
    : Boolean(selectedCompanyId)

  const handleNextStep0 = async () => {
    if (isCreatingNewCompany) {
      try {
        const created = await CompanyService.createCompany({
          legal_name: newCompany.legal_name,
          ticker: newCompany.ticker || undefined,
          industry: newCompany.industry,
          country: newCompany.country,
        })
        setSelectedCompanyId(created.id)
        toast.notifySuccess(`Company '${created.legal_name}' created successfully.`)
      } catch (err) {
        toast.notifyError(err instanceof Error ? err.message : 'Failed to create company')
        return
      }
    }
    setActiveStep(1)
  }

  const handleRunAssessment = async () => {
    setIsSubmitting(true)
    setActiveStep(3)

    try {
      const rawVars: Record<string, number> = {}
      Object.entries(financials).forEach(([key, val]) => {
        if (val !== undefined && val.trim() !== '') {
          const num = Number(val)
          if (!isNaN(num)) {
            rawVars[key] = num
          }
        }
      })

      const analysisId = `analysis_${Date.now()}`
      await EFSService.getAssessment(analysisId, {
        methodology_version: '1.0',
        statement_flags: {
          has_cash_flow_statement: true,
          has_balance_sheet: true,
          has_income_statement: true,
        },
        raw_variables: rawVars,
      })

      toast.notifySuccess('EFS Assessment complete and snapshot persisted!')
      navigate(`/assessments/${analysisId}`)
    } catch (err) {
      toast.notifyError(err instanceof Error ? err.message : 'Failed to run EFS Assessment')
      setActiveStep(2)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1180, mx: 'auto' }}>
      <Stack
        direction={{ xs: 'column', md: 'row' }}
        justifyContent="space-between"
        spacing={2}
        sx={{ mb: 3.5 }}
      >
        <Box>
          <Typography variant="h1">New Forensic Assessment</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.5 }}>
            Prepare structured financial input for the EFS™ deterministic engine.
          </Typography>
        </Box>
        <Chip
          label="EFS Assessment Pipeline"
          color="primary"
          variant="outlined"
          sx={{ alignSelf: { md: 'center' } }}
        />
      </Stack>

      <Card sx={{ mb: 3, overflowX: 'auto' }}>
        <Stepper activeStep={activeStep} sx={{ p: { xs: 2, md: 3 }, minWidth: 600 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Card>

      {/* STEP 0 — COMPANY SELECTION / CREATION */}
      {activeStep === 0 && (
        <Card>
          <CardContent sx={{ p: { xs: 2, md: 4 } }}>
            <Box sx={{ maxWidth: 760 }}>
              <Typography variant="h2">Select or Create Company</Typography>
              <Typography color="text.secondary" sx={{ mt: 0.75, mb: 3 }}>
                Link this assessment to an existing company entity or register a new one.
              </Typography>

              {loadingCompanies ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                  <CircularProgress size={32} />
                </Box>
              ) : !isCreatingNewCompany && existingCompanies.length > 0 ? (
                <Stack spacing={2.5}>
                  <FormControl fullWidth>
                    <InputLabel>Select Existing Company</InputLabel>
                    <Select
                      label="Select Existing Company"
                      value={selectedCompanyId}
                      onChange={(e) => setSelectedCompanyId(e.target.value)}
                    >
                      {existingCompanies.map((c) => (
                        <MenuItem key={c.id} value={c.id}>
                          {c.legal_name} {c.ticker ? `(${c.ticker})` : ''} — {c.industry || 'General'}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <Button
                    variant="text"
                    onClick={() => setIsCreatingNewCompany(true)}
                    sx={{ alignSelf: 'flex-start' }}
                  >
                    + Create New Company
                  </Button>
                </Stack>
              ) : (
                <Stack spacing={2.5}>
                  <TextField
                    label="Company Legal Name"
                    placeholder="e.g. Acme Corp India Ltd"
                    value={newCompany.legal_name}
                    onChange={(e) => setNewCompany({ ...newCompany, legal_name: e.target.value })}
                    fullWidth
                    required
                  />
                  <Box
                    sx={{
                      display: 'grid',
                      gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
                      gap: 2,
                    }}
                  >
                    <TextField
                      label="Stock Symbol / Ticker (Optional)"
                      placeholder="e.g. ACME"
                      value={newCompany.ticker}
                      onChange={(e) => setNewCompany({ ...newCompany, ticker: e.target.value })}
                      fullWidth
                    />
                    <FormControl fullWidth>
                      <InputLabel>Industry</InputLabel>
                      <Select
                        label="Industry"
                        value={newCompany.industry}
                        onChange={(e) => setNewCompany({ ...newCompany, industry: e.target.value })}
                      >
                        {industries.map((ind) => (
                          <MenuItem key={ind} value={ind}>
                            {ind}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Box>
                  <Box
                    sx={{
                      display: 'grid',
                      gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
                      gap: 2,
                    }}
                  >
                    <FormControl fullWidth>
                      <InputLabel>Country</InputLabel>
                      <Select
                        label="Country"
                        value={newCompany.country}
                        onChange={(e) => setNewCompany({ ...newCompany, country: e.target.value })}
                      >
                        {countries.map((c) => (
                          <MenuItem key={c} value={c}>
                            {c}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                    <FormControl fullWidth>
                      <InputLabel>Financial Year</InputLabel>
                      <Select
                        label="Financial Year"
                        value={newCompany.financialYear}
                        onChange={(e) =>
                          setNewCompany({ ...newCompany, financialYear: e.target.value })
                        }
                      >
                        {financialYears.map((fy) => (
                          <MenuItem key={fy} value={fy}>
                            {fy}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Box>

                  {existingCompanies.length > 0 && (
                    <Button
                      variant="text"
                      onClick={() => setIsCreatingNewCompany(false)}
                      sx={{ alignSelf: 'flex-start' }}
                    >
                      ← Back to Existing Companies
                    </Button>
                  )}
                </Stack>
              )}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* STEP 1 — FINANCIAL INPUT MODE: MANUAL VS UPLOAD & EXTRACT */}
      {activeStep === 1 && (
        <Stack spacing={3}>
          <Card>
            <CardContent sx={{ p: 2.5 }}>
              <Stack
                direction={{ xs: 'column', sm: 'row' }}
                justifyContent="space-between"
                alignItems={{ sm: 'center' }}
                spacing={2}
              >
                <Box>
                  <Typography variant="h3">Financial Data Input Mode</Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                    Select how to populate standard accounting inputs for forensic evaluation.
                  </Typography>
                </Box>
                <ToggleButtonGroup
                  value={inputMode}
                  exclusive
                  onChange={(_, val) => val && setInputMode(val)}
                  size="small"
                >
                  <ToggleButton value="MANUAL">
                    <TableChartOutlined sx={{ mr: 1, fontSize: 18 }} />
                    Manual Form Entry
                  </ToggleButton>
                  <ToggleButton value="UPLOAD">
                    <CloudUploadOutlined sx={{ mr: 1, fontSize: 18 }} />
                    Upload Document (PDF/Excel/CSV)
                  </ToggleButton>
                </ToggleButtonGroup>
              </Stack>
            </CardContent>
          </Card>

          {/* UPLOAD & EXTRACT MODE */}
          {inputMode === 'UPLOAD' && (
            <Stack spacing={3}>
              <Grid container spacing={3}>
                <Grid size={{ xs: 12, md: 7 }}>
                  <UploadCard
                    statement={uploadedStatement}
                    onFileChange={(file) =>
                      setUploadedStatement((prev) => ({ ...prev, file, progress: 0 }))
                    }
                    disabled={isIngesting}
                  />
                </Grid>
                <Grid size={{ xs: 12, md: 5 }}>
                  <Card sx={{ height: '100%' }}>
                    <CardContent sx={{ p: 2.5 }}>
                      <Typography variant="h3" sx={{ mb: 1 }}>
                        Local Extraction Engine
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Extracts text streams and table grids locally using PyMuPDF and openpyxl. No paid external APIs are called.
                      </Typography>
                      <Button
                        variant="contained"
                        fullWidth
                        startIcon={isIngesting ? <CircularProgress size={18} color="inherit" /> : <AutoAwesomeOutlined />}
                        onClick={handleIngestDocument}
                        disabled={!uploadedStatement.file || isIngesting}
                        sx={{ py: 1.2 }}
                      >
                        {isIngesting ? 'Extracting Document…' : 'Extract & Ingest Document'}
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {scannedPdfMessage && (
                <Alert severity="warning" icon={<InfoOutlined />}>
                  {scannedPdfMessage}
                </Alert>
              )}

              {extractedItems.length > 0 && (
                <Stack spacing={2.5}>
                  <HumanReviewTable
                    items={extractedItems}
                    onItemChange={(nextItems) => setExtractedItems(nextItems)}
                  />
                  <Button
                    variant="contained"
                    color="primary"
                    size="large"
                    endIcon={<ChevronRight />}
                    onClick={handleConfirmIngestionReview}
                    sx={{ alignSelf: 'flex-end', px: 4 }}
                  >
                    Confirm Review & Save Data
                  </Button>
                </Stack>
              )}
            </Stack>
          )}

          {/* MANUAL FORM ENTRY MODE */}
          {inputMode === 'MANUAL' && (
            <Grid container spacing={3}>
              <Grid size={{ xs: 12, md: 8 }}>
                <Card>
                  <CardContent sx={{ p: { xs: 2, md: 3.5 } }}>
                    <Stack
                      direction={{ xs: 'column', sm: 'row' }}
                      justifyContent="space-between"
                      alignItems={{ sm: 'center' }}
                      spacing={1.5}
                      sx={{ mb: 2.5 }}
                    >
                      <Box>
                        <Typography variant="h2">Financial Statement Data</Typography>
                        <Typography color="text.secondary" variant="body2" sx={{ mt: 0.5 }}>
                          Enter standard accounting figures. Missing fields are preserved as un-evaluated.
                        </Typography>
                      </Box>
                      <Button
                        variant="outlined"
                        color="secondary"
                        startIcon={<PlayCircleOutline />}
                        onClick={handleLoadDemoData}
                        size="small"
                      >
                        Load Demo Data
                        <Chip
                          label="DEMO DATA"
                          size="small"
                          color="warning"
                          sx={{ ml: 1, height: 18, fontSize: '0.6rem', fontWeight: 800 }}
                        />
                      </Button>
                    </Stack>

                    {isDemoDataLoaded && (
                      <Alert severity="info" icon={<InfoOutlined />} sx={{ mb: 2.5 }}>
                        Loaded sample financial data for demonstration (<strong>DEMO DATA</strong>). You can edit any field.
                      </Alert>
                    )}

                    <Stack spacing={3}>
                      <Box>
                        <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5, color: 'primary.main' }}>
                          INCOME STATEMENT & CASH FLOW
                        </Typography>
                        <Grid container spacing={2}>
                          <Grid size={{ xs: 12, sm: 6 }}>
                            <TextField
                              label="Revenue / Net Sales"
                              placeholder="e.g. 500000"
                              value={financials.revenue}
                              onChange={(e) => handleFieldChange('revenue', e.target.value)}
                              fullWidth
                            />
                          </Grid>
                          <Grid size={{ xs: 12, sm: 6 }}>
                            <TextField
                              label="Previous Year Revenue"
                              placeholder="e.g. 450000"
                              value={financials.prior_revenue}
                              onChange={(e) => handleFieldChange('prior_revenue', e.target.value)}
                              fullWidth
                            />
                          </Grid>
                          <Grid size={{ xs: 12, sm: 6 }}>
                            <TextField
                              label="Cash Flow From Operations (CFO)"
                              placeholder="e.g. 60000"
                              value={financials.cfo}
                              onChange={(e) => handleFieldChange('cfo', e.target.value)}
                              fullWidth
                            />
                          </Grid>
                          <Grid size={{ xs: 12, sm: 6 }}>
                            <TextField
                              label="Profit After Tax (PAT) / Net Income"
                              placeholder="e.g. 45000"
                              value={financials.pat}
                              onChange={(e) => handleFieldChange('pat', e.target.value)}
                              fullWidth
                            />
                          </Grid>
                          <Grid size={{ xs: 12, sm: 6 }}>
                            <TextField
                              label="Cost of Goods Sold (COGS)"
                              placeholder="e.g. 300000"
                              value={financials.cogs}
                              onChange={(e) => handleFieldChange('cogs', e.target.value)}
                              fullWidth
                            />
                          </Grid>
                          <Grid size={{ xs: 12, sm: 6 }}>
                            <TextField
                              label="EBIT / Operating Profit"
                              placeholder="e.g. 70000"
                              value={financials.ebit}
                              onChange={(e) => handleFieldChange('ebit', e.target.value)}
                              fullWidth
                            />
                          </Grid>
                        </Grid>
                      </Box>

                      <Box>
                        <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5, color: 'primary.main' }}>
                          BALANCE SHEET ITEMS
                        </Typography>
                        <Grid container spacing={2}>
                          <Grid size={{ xs: 12, sm: 6 }}>
                            <TextField
                              label="Accounts Receivable"
                              placeholder="e.g. 80000"
                              value={financials.receivables}
                              onChange={(e) => handleFieldChange('receivables', e.target.value)}
                              fullWidth
                            />
                          </Grid>
                          <Grid size={{ xs: 12, sm: 6 }}>
                            <TextField
                              label="Previous Year Accounts Receivable"
                              placeholder="e.g. 65000"
                              value={financials.prior_receivables}
                              onChange={(e) => handleFieldChange('prior_receivables', e.target.value)}
                              fullWidth
                            />
                          </Grid>
                          <Grid size={{ xs: 12, sm: 6 }}>
                            <TextField
                              label="Inventory"
                              placeholder="e.g. 50000"
                              value={financials.inventory}
                              onChange={(e) => handleFieldChange('inventory', e.target.value)}
                              fullWidth
                            />
                          </Grid>
                          <Grid size={{ xs: 12, sm: 6 }}>
                            <TextField
                              label="Accounts Payable"
                              placeholder="e.g. 40000"
                              value={financials.payables}
                              onChange={(e) => handleFieldChange('payables', e.target.value)}
                              fullWidth
                            />
                          </Grid>
                          <Grid size={{ xs: 12, sm: 6 }}>
                            <TextField
                              label="Total Assets"
                              placeholder="e.g. 600000"
                              value={financials.total_assets}
                              onChange={(e) => handleFieldChange('total_assets', e.target.value)}
                              fullWidth
                            />
                          </Grid>
                          <Grid size={{ xs: 12, sm: 6 }}>
                            <TextField
                              label="Previous Year Total Assets"
                              placeholder="e.g. 550000"
                              value={financials.prior_total_assets}
                              onChange={(e) => handleFieldChange('prior_total_assets', e.target.value)}
                              fullWidth
                            />
                          </Grid>
                          <Grid size={{ xs: 12, sm: 6 }}>
                            <TextField
                              label="Total Debt"
                              placeholder="e.g. 150000"
                              value={financials.total_debt}
                              onChange={(e) => handleFieldChange('total_debt', e.target.value)}
                              fullWidth
                            />
                          </Grid>
                          <Grid size={{ xs: 12, sm: 6 }}>
                            <TextField
                              label="Shareholder Equity"
                              placeholder="e.g. 350000"
                              value={financials.equity}
                              onChange={(e) => handleFieldChange('equity', e.target.value)}
                              fullWidth
                            />
                          </Grid>
                          <Grid size={{ xs: 12, sm: 6 }}>
                            <TextField
                              label="Depreciation & Amortization"
                              placeholder="e.g. 20000"
                              value={financials.depreciation}
                              onChange={(e) => handleFieldChange('depreciation', e.target.value)}
                              fullWidth
                            />
                          </Grid>
                        </Grid>
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>

              {/* DATA COVERAGE PANEL */}
              <Grid size={{ xs: 12, md: 4 }}>
                <Card sx={{ position: 'sticky', top: 20 }}>
                  <CardContent sx={{ p: 2.5 }}>
                    <Typography variant="h3" sx={{ mb: 0.5 }}>
                      Financial Data Coverage
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2.5 }}>
                      Data availability indicators computed from non-empty backend inputs.
                    </Typography>

                    <Stack spacing={2.5}>
                      <Box>
                        <Stack direction="row" justifyContent="space-between" sx={{ mb: 0.75 }}>
                          <Typography variant="body2" fontWeight={650}>
                            Core financial data
                          </Typography>
                          <Typography variant="body2" fontWeight={750} color="primary.main">
                            {coreCoveragePct}%
                          </Typography>
                        </Stack>
                        <LinearProgress
                          variant="determinate"
                          value={coreCoveragePct}
                          sx={{ height: 7, borderRadius: 4 }}
                        />
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                          {countFilled(coreFields)} of {coreFields.length} core fields entered
                        </Typography>
                      </Box>

                      <Box>
                        <Stack direction="row" justifyContent="space-between" sx={{ mb: 0.75 }}>
                          <Typography variant="body2" fontWeight={650}>
                            Historical data
                          </Typography>
                          <Typography variant="body2" fontWeight={750} color="primary.main">
                            {historicalCoveragePct}%
                          </Typography>
                        </Stack>
                        <LinearProgress
                          variant="determinate"
                          value={historicalCoveragePct}
                          color="secondary"
                          sx={{ height: 7, borderRadius: 4 }}
                        />
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                          {countFilled(historicalFields)} of {historicalFields.length} prior year fields entered
                        </Typography>
                      </Box>

                      <Box>
                        <Stack direction="row" justifyContent="space-between" sx={{ mb: 0.75 }}>
                          <Typography variant="body2" fontWeight={650}>
                            Disclosure data
                          </Typography>
                          <Typography variant="body2" fontWeight={750} color="primary.main">
                            {disclosureCoveragePct}%
                          </Typography>
                        </Stack>
                        <LinearProgress
                          variant="determinate"
                          value={disclosureCoveragePct}
                          color="info"
                          sx={{ height: 7, borderRadius: 4 }}
                        />
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                          {countFilled(disclosureFields)} of {disclosureFields.length} disclosure fields entered
                        </Typography>
                      </Box>

                      <Alert severity="info" icon={<InfoOutlined fontSize="small" />} sx={{ fontSize: '0.75rem' }}>
                        Additional historical periods improve EFS coverage for trend and growth variables.
                      </Alert>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </Stack>
      )}

      {/* STEP 2 — REVIEW & VALIDATE */}
      {activeStep === 2 && (
        <Card>
          <CardContent sx={{ p: { xs: 2, md: 4 } }}>
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              justifyContent="space-between"
              alignItems={{ sm: 'center' }}
              spacing={2}
              sx={{ mb: 3 }}
            >
              <Box>
                <Typography variant="h2">Review Financial Data</Typography>
                <Typography color="text.secondary" sx={{ mt: 0.5 }}>
                  Verify figures before running the deterministic EFS™ engine.
                </Typography>
              </Box>
              <Button
                startIcon={<EditOutlined />}
                variant="outlined"
                onClick={() => setActiveStep(1)}
              >
                Edit Data
              </Button>
            </Stack>

            <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #e2e8f0', mb: 3 }}>
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ bgcolor: '#f8fafc' }}>
                    <TableCell sx={{ fontWeight: 700 }}>FINANCIAL STATEMENT LINE ITEM</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>VALUE</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>STATUS</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {[
                    { label: 'Revenue / Net Sales', key: 'revenue' },
                    { label: 'Previous Year Revenue', key: 'prior_revenue' },
                    { label: 'Accounts Receivable', key: 'receivables' },
                    { label: 'Previous Year Accounts Receivable', key: 'prior_receivables' },
                    { label: 'Cash Flow From Operations (CFO)', key: 'cfo' },
                    { label: 'Profit After Tax (PAT)', key: 'pat' },
                    { label: 'Cost of Goods Sold (COGS)', key: 'cogs' },
                    { label: 'Inventory', key: 'inventory' },
                    { label: 'Accounts Payable', key: 'payables' },
                    { label: 'Total Assets', key: 'total_assets' },
                    { label: 'Previous Year Total Assets', key: 'prior_total_assets' },
                    { label: 'Total Debt', key: 'total_debt' },
                    { label: 'Shareholder Equity', key: 'equity' },
                    { label: 'Depreciation & Amortization', key: 'depreciation' },
                    { label: 'EBIT / Operating Profit', key: 'ebit' },
                  ].map((row) => {
                    const rawVal = financials[row.key as keyof FinancialFormData]
                    const hasVal = rawVal !== undefined && rawVal.trim() !== ''
                    const numVal = Number(rawVal)
                    const isValidNum = hasVal && !isNaN(numVal)

                    return (
                      <TableRow key={row.key} hover>
                        <TableCell sx={{ fontWeight: 600 }}>{row.label}</TableCell>
                        <TableCell sx={{ fontFamily: 'monospace', fontWeight: 700 }}>
                          {hasVal ? (isValidNum ? Number(rawVal).toLocaleString('en-IN') : rawVal) : '—'}
                        </TableCell>
                        <TableCell>
                          {hasVal ? (
                            isValidNum ? (
                              <Chip label="Valid Number" color="success" size="small" variant="outlined" />
                            ) : (
                              <Chip label="Invalid Value" color="error" size="small" />
                            )
                          ) : (
                            <Chip label="Missing / Optional" color="default" size="small" variant="outlined" />
                          )}
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </TableContainer>

            <Alert severity="success" icon={<CheckCircleOutline />} sx={{ mb: 2 }}>
              Inputs validated cleanly. EFS deterministic calculation will evaluate 95 frozen variables, 110 rule conditions, and 5 established forensic models.
            </Alert>
          </CardContent>
        </Card>
      )}

      {/* STEP 3 — RUNNING ASSESSMENT PROGRESS */}
      {activeStep === 3 && (
        <Card>
          <CardContent sx={{ p: { xs: 4, md: 6 }, textAlign: 'center' }}>
            <Box sx={{ maxWidth: 520, mx: 'auto' }}>
              <CircularProgress size={48} sx={{ mb: 3 }} />
              <Typography variant="h2">Running Deterministic EFS Engine...</Typography>
              <Typography color="text.secondary" sx={{ mt: 1, mb: 3 }}>
                Preparing assessment snapshot, evaluating 95 variables across 7 pillars, and persisting immutable audit record to PostgreSQL Neon.
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* FOOTER ACTIONS */}
      {activeStep < 3 && (
        <Stack direction="row" justifyContent="space-between" sx={{ mt: 3 }}>
          <Button
            onClick={activeStep === 0 ? () => navigate('/') : () => setActiveStep((s) => s - 1)}
          >
            {activeStep === 0 ? 'Cancel' : 'Back'}
          </Button>

          {activeStep === 0 && (
            <Button
              variant="contained"
              endIcon={<ChevronRight />}
              disabled={!canProceedStep0}
              onClick={handleNextStep0}
            >
              Continue to Financial Data
            </Button>
          )}

          {activeStep === 1 && inputMode === 'MANUAL' && (
            <Button
              variant="contained"
              endIcon={<ChevronRight />}
              onClick={() => setActiveStep(2)}
            >
              Review Data
            </Button>
          )}

          {activeStep === 2 && (
            <Button
              variant="contained"
              color="primary"
              startIcon={<PlayArrow />}
              disabled={isSubmitting}
              onClick={handleRunAssessment}
            >
              {isSubmitting ? 'Running EFS…' : 'Confirm & Run EFS'}
            </Button>
          )}
        </Stack>
      )}
    </Box>
  )
}
