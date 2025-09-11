import React from 'react'

const HomePage: React.FC = () => {
  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Background Video */}
      <video
        autoPlay
        loop
        muted
        className="absolute top-0 left-0 z-0 object-cover w-full h-full"
      >
        <source src="https://ik.imagekit.io/fwqphsval/The_truck_and_202509050015.mp4?updatedAt=1757588061724" type="video/mp4" />
      </video>
      
      {/* Overlay for better text readability */}
      <div className="absolute top-0 left-0 z-10 w-full h-full bg-black bg-opacity-0"></div>
      
      {/* Content */}
      <div className="container relative z-20 px-4 py-16 mx-auto">
        <div className="mb-12 text-center">
          <h1 className="mb-6 text-5xl font-bold text-white">
            Hybrid Quantum-Classical Supply Chain Optimization
          </h1>
          <p className="max-w-3xl mx-auto text-xl text-gray-200">
            Revolutionary supply chain optimization platform that combines quantum computing algorithms 
            with classical optimization techniques to achieve superior performance in cost reduction, 
            carbon footprint minimization, and delivery time optimization.
          </p>
        </div>

        <div className="grid gap-8 mb-16 md:grid-cols-3">
          <div className="p-6 bg-slate-800 rounded-lg shadow-lg bg-opacity-90 card-hover border border-slate-700">
            <div className="flex items-center justify-center w-12 h-12 mb-4 bg-blue-900/50 rounded-lg border border-blue-600">
              <span className="text-2xl">🔬</span>
            </div>
            <h3 className="mb-3 text-xl font-semibold text-slate-200">Quantum-Enhanced Optimization</h3>
            <p className="text-slate-300">
              Leverage QAOA (Quantum Approximate Optimization Algorithm) for combinatorial route selection
            </p>
          </div>

          <div className="p-6 bg-slate-800 rounded-lg shadow-lg bg-opacity-90 card-hover border border-slate-700">
            <div className="flex items-center justify-center w-12 h-12 mb-4 bg-purple-900/50 rounded-lg border border-purple-600">
              <span className="text-2xl">🎯</span>
            </div>
            <h3 className="mb-3 text-xl font-semibold text-slate-200">Classical Linear Programming</h3>
            <p className="text-slate-300">
              Robust optimization using OR-Tools and PuLP for continuous variables
            </p>
          </div>

          <div className="p-6 bg-slate-800 rounded-lg shadow-lg bg-opacity-90 card-hover border border-slate-700">
            <div className="flex items-center justify-center w-12 h-12 mb-4 bg-green-900/50 rounded-lg border border-green-600">
              <span className="text-2xl">🔀</span>
            </div>
            <h3 className="mb-3 text-xl font-semibold text-slate-200">Hybrid Architecture</h3>
            <p className="text-slate-300">
              Intelligent combination of quantum and classical approaches for optimal performance
            </p>
          </div>
        </div>

        <div className="text-center">
          <button className="mr-4 btn-quantum">
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
