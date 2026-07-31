import { createTheme } from '@mui/material/styles'

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#635bff', dark: '#4f46d8', light: '#827cff' },
    secondary: { main: '#0f766e' },
    background: { default: '#f7f8fc', paper: '#ffffff' },
    text: { primary: '#172033', secondary: '#697386' },
    divider: '#e7eaf0',
    success: { main: '#0f9f72' },
    warning: { main: '#d98b10' },
    error: { main: '#d94f5c' },
  },
  typography: {
    fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    h1: { fontSize: '2rem', fontWeight: 700, letterSpacing: '-0.04em' },
    h2: { fontSize: '1.5rem', fontWeight: 700, letterSpacing: '-0.03em' },
    h3: { fontSize: '1.125rem', fontWeight: 700 },
    body2: { fontSize: '0.8125rem' },
    caption: { fontSize: '0.6875rem', fontWeight: 600, letterSpacing: '0.04em' },
  },
  shape: { borderRadius: 10 },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        '*': { boxSizing: 'border-box' },
        body: { margin: 0, backgroundColor: '#f7f8fc' },
        button: { textTransform: 'none' },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: { border: '1px solid #e7eaf0', boxShadow: '0 2px 8px rgba(23, 32, 51, 0.025)' },
      },
    },
    MuiButton: { defaultProps: { disableElevation: true } },
  },
})
