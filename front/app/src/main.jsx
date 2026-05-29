import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { FeatureFlagProvider } from './context/FeatureFlagContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <FeatureFlagProvider>
      <App />
    </FeatureFlagProvider>
  </StrictMode>,
)
