import { useRef, useState } from 'react'
import { CloudUploadOutlined, DescriptionOutlined, DeleteOutline, UploadFileOutlined } from '@mui/icons-material'
import { Box, Button, Card, CardContent, LinearProgress, Stack, Typography } from '@mui/material'
import type { UploadedStatement } from '../types'

const acceptedExtensions = ['.xlsx', '.xls', '.csv']

function formatFileSize(bytes: number) {
  return bytes < 1024 * 1024 ? `${Math.max(1, Math.round(bytes / 1024))} KB` : `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

interface UploadCardProps {
  statement: UploadedStatement
  onFileChange: (file: File | null) => void
  disabled?: boolean
}

export function UploadCard({ statement, onFileChange, disabled = false }: UploadCardProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  const acceptFile = (file?: File) => {
    if (disabled) return
    if (file && acceptedExtensions.some((extension) => file.name.toLowerCase().endsWith(extension))) onFileChange(file)
  }

  return <Card sx={{ height: '100%', borderColor: dragging ? 'primary.main' : 'divider', backgroundColor: dragging ? 'rgba(99,91,255,.035)' : 'background.paper' }} onDragOver={(event) => { event.preventDefault(); setDragging(true) }} onDragLeave={() => setDragging(false)} onDrop={(event) => { event.preventDefault(); setDragging(false); acceptFile(event.dataTransfer.files[0]) }}>
    <CardContent sx={{ p: 2.5, '&:last-child': { pb: 2.5 } }}>
      <Stack direction="row" spacing={1.25} alignItems="center" sx={{ mb: 2.5 }}><Box sx={{ display: 'grid', placeItems: 'center', width: 34, height: 34, borderRadius: 1.5, bgcolor: 'rgba(99,91,255,.1)', color: 'primary.main' }}><DescriptionOutlined fontSize="small" /></Box><Box><Typography fontWeight={700} fontSize=".9rem">{statement.type}</Typography><Typography variant="caption" color="text.secondary">Excel or CSV · Max 25 MB</Typography></Box></Stack>
      {statement.file ? <Stack spacing={1.5}><Stack direction="row" spacing={1} alignItems="center"><UploadFileOutlined color="primary" fontSize="small" /><Box sx={{ minWidth: 0, flex: 1 }}><Typography noWrap fontSize=".78rem" fontWeight={700}>{statement.file.name}</Typography><Typography variant="caption" color="text.secondary">{formatFileSize(statement.file.size)}</Typography></Box><Button color="error" size="small" onClick={() => onFileChange(null)} startIcon={<DeleteOutline fontSize="small" />} disabled={disabled}>Remove</Button></Stack><LinearProgress variant="determinate" value={statement.progress} sx={{ height: 5, borderRadius: 3 }} /><Typography variant="caption" color="success.main">{statement.progress === 100 ? 'Upload complete' : `Uploading ${statement.progress}%`}</Typography></Stack> : <Stack alignItems="center" spacing={1.25} sx={{ py: 2.5, border: '1px dashed', borderColor: 'divider', borderRadius: 2 }}><CloudUploadOutlined sx={{ color: 'text.secondary', fontSize: 30 }} /><Typography variant="body2" color="text.secondary" textAlign="center">Drag and drop your file here</Typography><Button variant="outlined" size="small" onClick={() => inputRef.current?.click()} disabled={disabled}>Browse file</Button><input ref={inputRef} hidden type="file" accept=".xlsx,.xls,.csv" onChange={(event) => acceptFile(event.target.files?.[0])} /></Stack>}
    </CardContent>
  </Card>
}
