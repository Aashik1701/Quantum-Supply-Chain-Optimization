import React from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { RootState, AppDispatch } from '../../store'
import { runOptimization, stopOptimization, runVRPOptimization, runHybridVRPOptimization } from '../../store/optimizationSlice'
import MethodSelector from './MethodSelector'
import ParameterConfig from './ParameterConfig'
import OptimizationProgress from './OptimizationProgress'

interface OptimizationPanelProps {
  onOptimize?: () => void
}

const OptimizationPanel: React.FC<OptimizationPanelProps> = ({ onOptimize }) => {
  const dispatch = useDispatch<AppDispatch>()
  const { 
    isRunning, 
    progress, 
    selectedMethod, 
    parameters, 
    error 
  } = useSelector((state: RootState) => state.optimization)

  // Get data from data slice
  const { warehouses, customers, routes } = useSelector((state: RootState) => state.data)

  const handleStartOptimization = async () => {
    if (isRunning) {
      dispatch(stopOptimization())
    } else {
      try {
        if (selectedMethod === 'vrp') {
          await dispatch(runVRPOptimization({ 
            warehouses,
            customers,
            routes 
          })).unwrap()
        } else if (selectedMethod === 'hybrid-vrp') {
          await dispatch(runHybridVRPOptimization({ 
            warehouses,
            customers,
            routes 
          })).unwrap()
        } else {
          await dispatch(runOptimization({ 
            method: selectedMethod, 
            parameters,
            warehouses,
            customers,
            routes 
          })).unwrap()
        }
        if (onOptimize) {
          onOptimize()
        }
      } catch (error) {
        console.error('Optimization failed:', error)
      }
    }
  }

  return (
    <div className="bg-slate-800 rounded-lg shadow-md p-6 border border-slate-700">
      <h2 className="text-2xl font-bold text-slate-200 mb-6">Optimization Settings</h2>
      
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}

      <div className="space-y-6">
        {/* Method Selection */}
        <div>
          <MethodSelector />
        </div>

        {/* Parameters Configuration */}
        <div>
          <ParameterConfig />
        </div>

        {/* Progress Display */}
        {isRunning && (
          <div>
            <OptimizationProgress progress={progress} isRunning={isRunning} />
          </div>
        )}

        {/* Action Button */}
        <div className="flex justify-center pt-4">
          <button
            onClick={handleStartOptimization}
            disabled={false} // You can add validation logic here
            className={`
              px-8 py-3 rounded-lg font-medium text-white
              ${isRunning 
                ? 'bg-red-600 hover:bg-red-700' 
                : 'bg-blue-600 hover:bg-blue-700'
              }
              disabled:bg-gray-400 disabled:cursor-not-allowed
              transition-colors duration-200
            `}
          >
            {isRunning ? 'Stop Optimization' : 'Start Optimization'}
          </button>
        </div>

        {/* Method Information */}
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium text-slate-200 mb-2">Selected Method: {selectedMethod}</h4>
          <p className="text-sm text-gray-600">
            {selectedMethod === 'hybrid' && 'Combines classical and quantum algorithms for optimal results.'}
            {selectedMethod === 'quantum' && 'Uses Quantum Approximate Optimization Algorithm (QAOA).'}
            {selectedMethod === 'classical' && 'Uses classical linear programming with OR-Tools.'}
            {selectedMethod === 'vrp' && 'Vehicle Routing Problem optimization using OR-Tools for route planning.'}
            {selectedMethod === 'hybrid-vrp' && 'Advanced VRP with hybrid quantum-classical optimization algorithms.'}
          </p>
        </div>
      </div>
    </div>
  )
}

export default OptimizationPanel