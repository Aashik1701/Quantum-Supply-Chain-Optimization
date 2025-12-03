import { useCallback } from 'react'
import { toast as sonnerToast } from 'sonner'

export type ToastType = 'success' | 'error' | 'info' | 'warning' | 'loading'

interface ToastOptions {
  title?: string
  description?: string
  duration?: number
}

export function useToast() {
  const toast = useCallback((type: ToastType, options: ToastOptions) => {
    const { title, description, duration = 3000 } = options

    switch (type) {
      case 'success':
        sonnerToast.success(title || 'Success', {
          description,
          duration,
        })
        break
      case 'error':
        sonnerToast.error(title || 'Error', {
          description,
          duration,
        })
        break
      case 'info':
        sonnerToast.info(title || 'Info', {
          description,
          duration,
        })
        break
      case 'warning':
        sonnerToast.warning(title || 'Warning', {
          description,
          duration,
        })
        break
      case 'loading':
        sonnerToast.loading(title || 'Loading...', {
          description,
        })
        break
    }
  }, [])

  return {
    success: (options: ToastOptions) => toast('success', options),
    error: (options: ToastOptions) => toast('error', options),
    info: (options: ToastOptions) => toast('info', options),
    warning: (options: ToastOptions) => toast('warning', options),
    loading: (options: ToastOptions) => toast('loading', options),
  }
}
