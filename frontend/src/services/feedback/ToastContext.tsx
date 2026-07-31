import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'
import { Alert, Snackbar, type AlertColor } from '@mui/material'

interface Toast {
  id: number
  message: string
  severity: AlertColor
}

interface ToastContextValue {
  notify: (message: string, severity?: AlertColor) => void
  notifySuccess: (message: string) => void
  notifyError: (message: string) => void
}

const ToastContext = createContext<ToastContextValue | null>(null)

let toastId = 0

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const dismiss = useCallback((id: number) => {
    setToasts((current) => current.filter((toast) => toast.id !== id))
  }, [])

  const notify = useCallback((message: string, severity: AlertColor = 'info') => {
    const id = ++toastId
    setToasts((current) => [...current, { id, message, severity }])
  }, [])

  const value = useMemo<ToastContextValue>(() => ({
    notify,
    notifySuccess: (message: string) => notify(message, 'success'),
    notifyError: (message: string) => notify(message, 'error'),
  }), [notify])

  return (
    <ToastContext.Provider value={value}>
      {children}
      {toasts.map((toast) => (
        <Snackbar
          key={toast.id}
          open
          autoHideDuration={6000}
          onClose={() => dismiss(toast.id)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert
            onClose={() => dismiss(toast.id)}
            severity={toast.severity}
            variant="filled"
            sx={{ width: '100%' }}
          >
            {toast.message}
          </Alert>
        </Snackbar>
      ))}
    </ToastContext.Provider>
  )
}

export function useToast(): ToastContextValue {
  const context = useContext(ToastContext)
  if (!context) throw new Error('useToast must be used within a ToastProvider')
  return context
}
