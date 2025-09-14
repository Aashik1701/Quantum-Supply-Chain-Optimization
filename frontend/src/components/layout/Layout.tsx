import React from 'react'
import BackgroundVideo from './BackgroundVideo'
import { useLocation } from 'react-router-dom'
import { getBackgroundForPath } from '@/config/pageBackgrounds'

interface LayoutProps {
  children: React.ReactNode
  /** Optional background video URL for the entire page */
  bgVideoSrc?: string
  /** Add a dark overlay when bg video is enabled */
  bgVideoOverlay?: boolean
}

const Layout: React.FC<LayoutProps> = ({ children, bgVideoSrc, bgVideoOverlay = false }) => {
  const location = useLocation()
  const autoBg = getBackgroundForPath(location.pathname)
  return (
    <div className="relative min-h-screen bg-slate-900 overflow-hidden">
      {(bgVideoSrc || autoBg) && (
        <BackgroundVideo src={bgVideoSrc || autoBg!} withOverlay={bgVideoOverlay || true} />
      )}
      <header className="bg-slate-800 shadow-lg border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-white">
                Quantum Supply Chain
              </h1>
            </div>
            <nav className="flex space-x-8">
              <a href="/" className="text-slate-300 hover:text-white transition-colors">Home</a>
              <a href="/dashboard" className="text-slate-300 hover:text-white transition-colors">Dashboard</a>
              <a href="/optimization" className="text-slate-300 hover:text-white transition-colors">Optimization</a>
              <a href="/data" className="text-slate-300 hover:text-white transition-colors">Data</a>
              <a href="/results" className="text-slate-300 hover:text-white transition-colors">Results</a>
            </nav>
          </div>
        </div>
      </header>
      
      <main className="relative flex-1 bg-slate-900 z-10">
        {children}
      </main>
      
      <footer className="bg-slate-800 border-t border-slate-700">
        <div className="px-4 py-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
          <p className="text-sm text-center text-slate-400">
            © 2025 Quantum Supply Chain Optimization. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Layout
