import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import {
  Addchart, AssessmentOutlined, Bolt, BookmarkBorder, DashboardOutlined,
  ExpandLess, ExpandMore, History, NotificationsNone, SettingsOutlined,
  CompareArrows,
} from '@mui/icons-material'
import { Box, Collapse, Divider, IconButton, List, ListItemButton, ListItemIcon, ListItemText, Stack, Typography } from '@mui/material'

const primaryItems = [
  { label: 'Dashboard', path: '/', icon: <DashboardOutlined /> },
  { label: 'New Analysis', path: '/analysis/new', icon: <Addchart /> },
  { label: 'History', path: '/history', icon: <History /> },
  { label: 'Compare', path: '/compare', icon: <CompareArrows /> },
]

const workspaceItems = [
  { label: 'Watchlist', path: '/watchlist', icon: <BookmarkBorder /> },
  { label: 'Reports', path: '/reports', icon: <AssessmentOutlined /> },
  { label: 'Alerts', path: '/alerts', icon: <NotificationsNone /> },
]

export function Sidebar({ mobileOpen, onClose }: { mobileOpen: boolean; onClose: () => void }) {
  const [workspaceOpen, setWorkspaceOpen] = useState(true)
  const drawerWidth = 248

  const nav = (items: typeof primaryItems) => items.map((item) => (
    <ListItemButton
      key={item.path}
      component={NavLink}
      to={item.path}
      end={item.path === '/'}
      onClick={onClose}
      sx={{ '&.active': { backgroundColor: 'rgba(99, 91, 255, .1)', color: 'primary.main', '& .MuiListItemIcon-root': { color: 'primary.main' } } }}
    >
      <ListItemIcon>{item.icon}</ListItemIcon>
      <ListItemText primary={item.label} />
    </ListItemButton>
  ))

  return (
    <Box component="aside" sx={{ width: { md: drawerWidth }, flexShrink: 0 }}>
      <Box onClick={onClose} sx={{ display: { xs: mobileOpen ? 'block' : 'none', md: 'none' }, position: 'fixed', inset: 0, zIndex: 1199, bgcolor: 'rgba(15, 23, 42, .35)' }} />
      <Box sx={{ width: drawerWidth, display: { xs: mobileOpen ? 'flex' : 'none', md: 'flex' }, flexDirection: 'column', position: { xs: 'fixed', md: 'fixed' }, zIndex: 1200, top: 0, bottom: 0, left: 0, bgcolor: 'background.paper', borderRight: 1, borderColor: 'divider' }}>
        <Stack direction="row" alignItems="center" spacing={1.25} sx={{ px: 2.5, height: 72 }}>
          <Box sx={{ width: 30, height: 30, display: 'grid', placeItems: 'center', borderRadius: 1.5, bgcolor: 'primary.main', color: '#fff' }}><Bolt sx={{ fontSize: 18 }} /></Box>
          <Box>
            <Typography fontWeight={800} fontSize=".95rem" lineHeight={1.1}>EarningsGuard</Typography>
            <Typography variant="caption" color="text.secondary">AI INTELLIGENCE</Typography>
          </Box>
          <IconButton onClick={onClose} size="small" sx={{ ml: 'auto', display: { md: 'none' } }}>×</IconButton>
        </Stack>
        <Divider />
        <List disablePadding sx={{ px: 1.5, pt: 2 }}>{nav(primaryItems)}</List>
        <Stack direction="row" alignItems="center" sx={{ px: 2.5, pt: 3, pb: 1 }}>
          <Typography variant="caption" color="text.secondary">WORKSPACE</Typography>
          <IconButton size="small" onClick={() => setWorkspaceOpen((open) => !open)} sx={{ ml: 'auto' }}>{workspaceOpen ? <ExpandLess fontSize="small" /> : <ExpandMore fontSize="small" />}</IconButton>
        </Stack>
        <Collapse in={workspaceOpen}><List disablePadding sx={{ px: 1.5 }}>{nav(workspaceItems)}</List></Collapse>
        <Box sx={{ mt: 'auto' }}><Divider /><List disablePadding sx={{ p: 1.5 }}>{nav([{ label: 'Settings', path: '/settings', icon: <SettingsOutlined /> }])}</List></Box>
      </Box>
    </Box>
  )
}
