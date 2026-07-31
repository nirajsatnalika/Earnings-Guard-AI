import { Menu, NotificationsNone, Search } from '@mui/icons-material'
import { Avatar, Badge, Box, IconButton, InputAdornment, TextField, Typography } from '@mui/material'

export function Topbar({ onMenuClick }: { onMenuClick: () => void }) {
  return (
    <Box component="header" sx={{ height: 72, px: { xs: 2, md: 4 }, display: 'flex', alignItems: 'center', bgcolor: 'background.paper', borderBottom: 1, borderColor: 'divider' }}>
      <IconButton onClick={onMenuClick} sx={{ display: { md: 'none' }, mr: 1 }} aria-label="Open navigation"><Menu /></IconButton>
      <TextField placeholder="Search companies, filings, or reports" size="small" sx={{ width: { xs: '100%', sm: 360 }, '& .MuiOutlinedInput-root': { bgcolor: '#f7f8fc', borderRadius: 2 } }} InputProps={{ startAdornment: <InputAdornment position="start"><Search sx={{ color: 'text.secondary', fontSize: 19 }} /></InputAdornment> }} />
      <Box sx={{ ml: 'auto', display: 'flex', alignItems: 'center', gap: { xs: 1, md: 2 } }}>
        <Badge color="error" variant="dot" overlap="circular"><IconButton aria-label="Notifications"><NotificationsNone /></IconButton></Badge>
        <Box sx={{ display: { xs: 'none', sm: 'block' }, textAlign: 'right' }}><Typography fontSize=".8rem" fontWeight={700}>Alex Morgan</Typography><Typography variant="caption" color="text.secondary">Portfolio Manager</Typography></Box>
        <Avatar sx={{ width: 36, height: 36, bgcolor: '#172033', fontSize: '.8rem', fontWeight: 700 }}>AM</Avatar>
      </Box>
    </Box>
  )
}
