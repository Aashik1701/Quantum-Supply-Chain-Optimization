import React from 'react'
import BackgroundVideo from './BackgroundVideo'
import EnhancedNavbar from './EnhancedNavbar'
import { useLocation } from 'react-router-dom'
import { getBackgroundForPath } from '@/config/pageBackgrounds'
import { Toaster } from 'sonner'

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
      
      <EnhancedNavbar />
      
      <main className="relative flex-1 bg-slate-900 z-10 min-h-[calc(100vh-8rem)]">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          {children}
        </div>
      </main>
      
      <footer className="bg-slate-800 border-t border-slate-700">
        <div className="px-4 py-6 mx-auto max-w-7xl sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-slate-400">
              © 2025 Quantum Supply Chain Optimization. All rights reserved.
            </p>
            <div className="flex items-center space-x-6 text-sm text-slate-400">
              <a href="/about" className="hover:text-white transition-colors">About</a>
              <a href="https://github.com/Aashik1701/Quantum-Supply-Chain-Optimization" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">GitHub</a>
              <a href="/docs" className="hover:text-white transition-colors">Docs</a>
            </div>
          </div>
        </div>
      </footer>
      
      <Toaster 
        theme="dark"
        position="top-right"
        expand={true}
        richColors
      />
    </div>
  )
}

export default Layout
