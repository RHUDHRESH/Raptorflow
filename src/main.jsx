import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

import GlobalErrorBoundary from './components/system/GlobalErrorBoundary'

if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
  const maybeRegister = navigator.serviceWorker?.register
  if (typeof maybeRegister === 'function') {
    const originalRegister = maybeRegister.bind(navigator.serviceWorker)
    navigator.serviceWorker.register = (...args) =>
      originalRegister(...args).catch((err) => {
        console.warn('[sw] Service worker registration skipped in this environment:', err)
        return null
      })
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <GlobalErrorBoundary>
      <App />
    </GlobalErrorBoundary>
  </React.StrictMode>,
)
