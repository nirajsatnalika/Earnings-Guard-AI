import { useState } from 'react'
import { Box } from '@mui/material'
import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Topbar } from './Topbar'

export function AppShell() {
  const [mobileOpen, setMobileOpen] = useState(false)
  return <Box sx={{ minHeight: '100vh', display: 'flex' }}><Sidebar mobileOpen={mobileOpen} onClose={() => setMobileOpen(false)} /><Box sx={{ flex: 1, minWidth: 0, ml: { md: '248px' } }}><Topbar onMenuClick={() => setMobileOpen(true)} /><Box component="main"><Outlet /></Box></Box></Box>
}
