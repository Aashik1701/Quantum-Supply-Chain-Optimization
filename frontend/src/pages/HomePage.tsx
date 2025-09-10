import React from 'react'

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gradient mb-6">
            Hybrid Quantum-Classical Supply Chain Optimization
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Revolutionary supply chain optimization platform that combines quantum computing algorithms 
            with classical optimization techniques to achieve superior performance in cost reduction, 
            carbon footprint minimization, and delivery time optimization.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white rounded-lg shadow-lg p-6 card-hover">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">🔬</span>
            </div>
            <h3 className="text-xl font-semibold mb-3">Quantum-Enhanced Optimization</h3>
            <p className="text-gray-600">
              Leverage QAOA (Quantum Approximate Optimization Algorithm) for combinatorial route selection
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 card-hover">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">🎯</span>
            </div>
            <h3 className="text-xl font-semibold mb-3">Classical Linear Programming</h3>
            <p className="text-gray-600">
              Robust optimization using OR-Tools and PuLP for continuous variables
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 card-hover">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">🔀</span>
            </div>
            <h3 className="text-xl font-semibold mb-3">Hybrid Architecture</h3>
            <p className="text-gray-600">
              Intelligent combination of quantum and classical approaches for optimal performance
            </p>
          </div>
        </div>

        <div className="text-center">
          <button className="btn-quantum mr-4">
            Get Started
          </button>
          <button className="btn-secondary">
            View Demo
          </button>
        </div>
      </div>
    </div>
  )
}

export default HomePage
