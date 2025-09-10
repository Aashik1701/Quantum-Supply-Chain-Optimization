import React, { useState, useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { RootState, AppDispatch } from '../store'
import { 
  startOptimization, 
  stopOptimization, 
  updateParameters 
} from '../store/optimizationSlice'
import OptimizationPanel from '../components/optimization/OptimizationPanel'
import MethodSelector from '../components/optimization/MethodSelector'
import ParameterConfig from '../components/optimization/ParameterConfig'
import OptimizationProgress from '../components/optimization/OptimizationProgress'
import ResultsPanel from '../components/optimization/ResultsPanel'
import MapVisualization from '../components/visualization/MapVisualization'

const OptimizationPage: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>()
  const { 
    isRunning, 
    progress, 
    results, 
    parameters, 
    selectedMethod,
    error 
  } = useSelector((state: RootState) => state.optimization)
  const { warehouses, customers, routes } = useSelector((state: RootState) => state.data)

  const [activeTab, setActiveTab] = useState<'configure' | 'progress' | 'results'>('configure')

  useEffect(() => {
    if (isRunning && progress < 100) {
      setActiveTab('progress')
    } else if (results && !isRunning) {
      setActiveTab('results')
    }
  }, [isRunning, progress, results])

  const handleStartOptimization = () => {
    dispatch(startOptimization({
      method: selectedMethod,
      parameters,
      data: { warehouses, customers, routes }
    }))
  }

  const handleStopOptimization = () => {
    dispatch(stopOptimization())
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Supply Chain Optimization
        </h1>
        <p className="text-gray-600 mt-1">
          Configure and run quantum-classical hybrid optimization algorithms.
        </p>
      </div>

      {/* Main Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Control Panel */}
        <div className="lg:col-span-1 space-y-6">
          <OptimizationPanel
            isRunning={isRunning}
            onStart={handleStartOptimization}
            onStop={handleStopOptimization}
            error={error}
          />

          {/* Tab Navigation */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="border-b border-gray-200">
              <nav className="flex">
                {[
                  { id: 'configure', label: 'Configure', icon: '⚙️' },
                  { id: 'progress', label: 'Progress', icon: '📊' },
                  { id: 'results', label: 'Results', icon: '📈' }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex-1 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    <span className="mr-2">{tab.icon}</span>
                    {tab.label}
                  </button>
                ))}
              </nav>
            </div>

            <div className="p-6">
              {activeTab === 'configure' && (
                <div className="space-y-6">
                  <MethodSelector />
                  <ParameterConfig />
                </div>
              )}

              {activeTab === 'progress' && (
                <OptimizationProgress 
                  progress={progress}
                  isRunning={isRunning}
                />
              )}

              {activeTab === 'results' && (
                <ResultsPanel results={results} />
              )}
            </div>
          </div>
        </div>

        {/* Visualization Area */}
        <div className="lg:col-span-2 space-y-6">
          {/* Map Visualization */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Network Visualization
            </h2>
            <div className="h-96">
              <MapVisualization
                warehouses={warehouses}
                customers={customers}
                routes={results?.routes || routes}
                highlightOptimal={!!results}
              />
            </div>
          </div>

          {/* Results Summary */}
          {results && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Optimization Summary
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">
                    ${results.totalCost?.toLocaleString()}
                  </p>
                  <p className="text-sm text-gray-600">Total Cost</p>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">
                    {results.efficiency?.toFixed(1)}%
                  </p>
                  <p className="text-sm text-gray-600">Efficiency</p>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <p className="text-2xl font-bold text-purple-600">
                    {results.executionTime?.toFixed(2)}s
                  </p>
                  <p className="text-sm text-gray-600">Execution Time</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default OptimizationPage
