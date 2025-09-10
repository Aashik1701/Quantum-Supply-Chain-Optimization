import React from 'react'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">
                Quantum Supply Chain
              </h1>
            </div>
            <nav className="flex space-x-8">
              <a href="/" className="text-gray-500 hover:text-gray-900">Home</a>
              <a href="/dashboard" className="text-gray-500 hover:text-gray-900">Dashboard</a>
              <a href="/optimization" className="text-gray-500 hover:text-gray-900">Optimization</a>
              <a href="/data" className="text-gray-500 hover:text-gray-900">Data</a>
              <a href="/results" className="text-gray-500 hover:text-gray-900">Results</a>
            </nav>
          </div>
        </div>
      </header>
      
      <main className="flex-1">
        {children}
      </main>
      
      <footer className="bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-gray-500 text-sm">
            © 2024 Quantum Supply Chain Optimization. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Layout
