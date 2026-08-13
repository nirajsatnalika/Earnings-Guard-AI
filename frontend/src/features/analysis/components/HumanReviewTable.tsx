import { useState } from 'react'
import {
  CheckCircleOutlined,
  EditOutlined,
  HighlightOffOutlined,
  InfoOutlined,
  SwapHorizOutlined,
} from '@mui/icons-material'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  MenuItem,
  Select,
  Stack,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'
import type { CanonicalExtractedItem } from '../../../services/api'

interface HumanReviewTableProps {
  items: CanonicalExtractedItem[]
  onItemChange: (updatedItems: CanonicalExtractedItem[]) => void
}

const canonicalOptions = [
  'Revenue',
  'Prior Revenue',
  'Receivables',
  'Prior Receivables',
  'Operating Cash Flow',
  'PAT',
  'Cost of Goods Sold',
  'Inventory',
  'Trade Payables',
  'Total Assets',
  'Prior Total Assets',
  'Depreciation',
  'CapEx',
  'Total Debt',
  'Equity',
  'EBIT',
]

export function HumanReviewTable({ items, onItemChange }: HumanReviewTableProps) {
  const [activeTab, setActiveTab] = useState<'FINANCIAL' | 'DISCLOSURE' | 'GOVERNANCE' | 'PEER_EXTERNAL'>('FINANCIAL')

  // State for edit dialog
  const [editingItem, setEditingItem] = useState<CanonicalExtractedItem | null>(null)
  const [editValue, setEditValue] = useState<string>('')

  // State for remap dialog
  const [remappingItem, setRemappingItem] = useState<CanonicalExtractedItem | null>(null)
  const [selectedCanonical, setSelectedCanonical] = useState<string>('')

  const handleAction = (id: string, action: 'ACCEPT' | 'REJECT') => {
    const next = items.map((item) => {
      if (item.id === id) {
        return {
          ...item,
          review_status: action === 'ACCEPT' ? 'ACCEPTED' : 'REJECTED',
        }
      }
      return item
    })
    onItemChange(next)
  }

  const handleAcceptAllHighConfidence = () => {
    const next = items.map((item) => {
      if (
        item.review_status === 'PENDING' &&
        (item.mapping_status === 'EXACT_MATCH' || item.mapping_status === 'HIGH_CONFIDENCE_MATCH')
      ) {
        return { ...item, review_status: 'ACCEPTED' }
      }
      return item
    })
    onItemChange(next)
  }

  const handleSaveEdit = () => {
    if (!editingItem) return
    const num = Number(editValue)
    const next = items.map((item) => {
      if (item.id === editingItem.id) {
        return {
          ...item,
          normalized_value: isNaN(num) ? null : num,
          review_status: 'EDITED',
        }
      }
      return item
    })
    onItemChange(next)
    setEditingItem(null)
  }

  const handleSaveRemap = () => {
    if (!remappingItem) return
    const next = items.map((item) => {
      if (item.id === remappingItem.id) {
        return {
          ...item,
          canonical_field: selectedCanonical,
          review_status: 'EDITED',
        }
      }
      return item
    })
    onItemChange(next)
    setRemappingItem(null)
  }

  const getStatusChip = (mappingStatus: string) => {
    switch (mappingStatus) {
      case 'EXACT_MATCH':
        return <Chip label="Exact Match" color="success" size="small" variant="outlined" />
      case 'HIGH_CONFIDENCE_MATCH':
        return <Chip label="High Confidence" color="info" size="small" variant="outlined" />
      case 'REVIEW_REQUIRED':
        return <Chip label="Review Required" color="warning" size="small" />
      default:
        return <Chip label="Unmapped" color="default" size="small" variant="outlined" />
    }
  }

  const getReviewChip = (reviewStatus: string) => {
    switch (reviewStatus) {
      case 'ACCEPTED':
        return <Chip label="ACCEPTED" color="success" size="small" sx={{ fontWeight: 700 }} />
      case 'EDITED':
        return <Chip label="EDITED" color="primary" size="small" sx={{ fontWeight: 700 }} />
      case 'REJECTED':
        return <Chip label="REJECTED" color="error" size="small" sx={{ fontWeight: 700 }} />
      default:
        return <Chip label="PENDING" color="warning" size="small" variant="outlined" sx={{ fontWeight: 700 }} />
    }
  }

  return (
    <Card>
      <CardContent sx={{ p: { xs: 2, md: 3 } }}>
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          justifyContent="space-between"
          alignItems={{ sm: 'center' }}
          spacing={2}
          sx={{ mb: 2.5 }}
        >
          <Box>
            <Typography variant="h2">Human Verification & Data Provenance</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              Review extracted line items and source provenance before passing values to the deterministic EFS engine.
            </Typography>
          </Box>
          <Button
            variant="outlined"
            size="small"
            startIcon={<CheckCircleOutlined />}
            onClick={handleAcceptAllHighConfidence}
          >
            Accept High Confidence Matches
          </Button>
        </Stack>

        <Alert severity="info" icon={<InfoOutlined fontSize="small" />} sx={{ mb: 2.5, fontSize: '0.8rem' }}>
          Only <strong>ACCEPTED</strong> or <strong>EDITED</strong> line items will be passed into the assessment input payload. Missing or rejected items remain un-evaluated.
        </Alert>

        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={activeTab} onChange={(_, val) => setActiveTab(val)}>
            <Tab
              label={`Financial Statements (${items.filter((i) => !i.evidence_category || i.evidence_category === 'FINANCIAL_STATEMENT').length})`}
              value="FINANCIAL"
            />
            <Tab
              label={`Footnotes & Disclosures (${items.filter((i) => i.evidence_category === 'NOTE_DISCLOSURE').length})`}
              value="DISCLOSURE"
            />
            <Tab
              label={`Governance & Auditor (${items.filter((i) => i.evidence_category === 'GOVERNANCE_AUDITOR').length})`}
              value="GOVERNANCE"
            />
            <Tab
              label={`Peer & External Evidence (${items.filter((i) => i.evidence_category === 'PEER_EXTERNAL_INTELLIGENCE').length})`}
              value="PEER_EXTERNAL"
            />
          </Tabs>
        </Box>

        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: '#f8fafc' }}>
                <TableCell sx={{ fontWeight: 700 }}>DOCUMENT LINE ITEM & SOURCE</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>EXTRACTED VALUE / EVIDENCE</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>CANONICAL / EFS MAPPING</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>CONFIDENCE</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>STATUS</TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="right">
                  ACTIONS
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(() => {
                const displayItems = items.filter((i) => {
                  if (activeTab === 'DISCLOSURE') return i.evidence_category === 'NOTE_DISCLOSURE'
                  if (activeTab === 'GOVERNANCE') return i.evidence_category === 'GOVERNANCE_AUDITOR'
                  if (activeTab === 'PEER_EXTERNAL') return i.evidence_category === 'PEER_EXTERNAL_INTELLIGENCE'
                  return !i.evidence_category || i.evidence_category === 'FINANCIAL_STATEMENT'
                })

                if (displayItems.length === 0) {
                  return (
                    <TableRow>
                      <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                        <Typography color="text.secondary">No items found for this category.</Typography>
                      </TableCell>
                    </TableRow>
                  )
                }

                return displayItems.map((item) => (
                  <TableRow key={item.id} hover>
                    <TableCell>
                      <Typography fontSize=".84rem" fontWeight={650}>
                        {item.raw_label}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Source: {item.source_filename}{' '}
                        {item.source_page ? `(Page ${item.source_page})` : item.source_sheet ? `(${item.source_sheet})` : ''}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography fontFamily="monospace" fontSize=".85rem" fontWeight={700}>
                        {item.normalized_value !== null ? item.normalized_value.toLocaleString('en-IN') : item.raw_value}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Raw: "{item.raw_value}" {item.unit ? `· Unit: ${item.unit}` : ''}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography fontSize=".84rem" fontWeight={600} color="primary.main">
                        {item.canonical_field || 'Unmapped'}
                      </Typography>
                      {item.mapped_efs_variable && (
                        <Chip
                          label={item.mapped_efs_variable}
                          size="small"
                          color="secondary"
                          sx={{ height: 18, fontSize: '0.65rem', fontWeight: 800, mt: 0.25 }}
                        />
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography fontSize=".8rem" fontWeight={700}>
                        {item.confidence}%
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Stack spacing={0.5} alignItems="flex-start">
                        {getStatusChip(item.mapping_status)}
                        {getReviewChip(item.review_status)}
                      </Stack>
                    </TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                        <Button
                          size="small"
                          color="success"
                          variant={item.review_status === 'ACCEPTED' ? 'contained' : 'outlined'}
                          onClick={() => handleAction(item.id, 'ACCEPT')}
                          sx={{ minWidth: 32, p: 0.5 }}
                          title="Accept Item"
                        >
                          <CheckCircleOutlined fontSize="small" />
                        </Button>
                        <Button
                          size="small"
                          color="primary"
                          variant="outlined"
                          onClick={() => {
                            setEditingItem(item)
                            setEditValue(item.normalized_value !== null ? String(item.normalized_value) : item.raw_value)
                          }}
                          sx={{ minWidth: 32, p: 0.5 }}
                          title="Edit Value"
                        >
                          <EditOutlined fontSize="small" />
                        </Button>
                        <Button
                          size="small"
                          color="secondary"
                          variant="outlined"
                          onClick={() => {
                            setRemappingItem(item)
                            setSelectedCanonical(item.canonical_field || '')
                          }}
                          sx={{ minWidth: 32, p: 0.5 }}
                          title="Remap Field"
                        >
                          <SwapHorizOutlined fontSize="small" />
                        </Button>
                        <Button
                          size="small"
                          color="error"
                          variant={item.review_status === 'REJECTED' ? 'contained' : 'outlined'}
                          onClick={() => handleAction(item.id, 'REJECT')}
                          sx={{ minWidth: 32, p: 0.5 }}
                          title="Reject Item"
                        >
                          <HighlightOffOutlined fontSize="small" />
                        </Button>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))
              })()}
            </TableBody>
          </Table>
        </TableContainer>

        {/* EDIT VALUE DIALOG */}
        <Dialog open={Boolean(editingItem)} onClose={() => setEditingItem(null)}>
          <DialogTitle>Edit Extracted Value</DialogTitle>
          <DialogContent sx={{ minWidth: 320, pt: 1 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Modify the numeric value for <strong>{editingItem?.raw_label}</strong>:
            </Typography>
            <TextField
              label="Numeric Value"
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              fullWidth
              autoFocus
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setEditingItem(null)}>Cancel</Button>
            <Button variant="contained" onClick={handleSaveEdit}>
              Save & Approve
            </Button>
          </DialogActions>
        </Dialog>

        {/* REMAP DIALOG */}
        <Dialog open={Boolean(remappingItem)} onClose={() => setRemappingItem(null)}>
          <DialogTitle>Remap Canonical Field</DialogTitle>
          <DialogContent sx={{ minWidth: 340, pt: 1 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Select canonical field mapping for <strong>{remappingItem?.raw_label}</strong>:
            </Typography>
            <FormControl fullWidth size="small">
              <Select value={selectedCanonical} onChange={(e) => setSelectedCanonical(e.target.value)}>
                <MenuItem value="">
                  <em>Not Mapped</em>
                </MenuItem>
                {canonicalOptions.map((opt) => (
                  <MenuItem key={opt} value={opt}>
                    {opt}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setRemappingItem(null)}>Cancel</Button>
            <Button variant="contained" onClick={handleSaveRemap}>
              Save Mapping
            </Button>
          </DialogActions>
        </Dialog>
      </CardContent>
    </Card>
  )
}
