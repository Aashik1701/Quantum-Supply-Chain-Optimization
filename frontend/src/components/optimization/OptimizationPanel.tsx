import React from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { RootState, AppDispatch } from '../../store'
import { runOptimization, stopOptimization, runVRPOptimization, runHybridVRPOptimization } from '../../store/optimizationSlice'
import MethodSelector from './MethodSelector'
import ParameterConfig from './ParameterConfig'
import OptimizationProgress from './OptimizationProgress'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Alert, AlertDescription } from '../ui/alert'
import { Badge } from '../ui/badge'
import { Play, StopCircle, CheckCircle2, AlertTriangle, Database } from 'lucide-react'
import { useToast } from '../../hooks/useToast'

interface OptimizationPanelProps {
  onOptimize?: () => void
}

const OptimizationPanel: React.FC<OptimizationPanelProps> = ({ onOptimize }) => {
  const dispatch = useDispatch<AppDispatch>()
  const toast = useToast()
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
      toast.info({ 
        title: 'Optimization Stopped', 
        description: 'The optimization process has been cancelled.' 
      })
      return
    }

    // Validate that we have data
    if (!warehouses || warehouses.length === 0) {
      toast.error({ 
        title: 'No Warehouse Data', 
        description: 'Please add warehouse data first in the Data Management page.' 
      })
      return
    }
    if (!customers || customers.length === 0) {
      toast.error({ 
        title: 'No Customer Data', 
        description: 'Please add customer data first in the Data Management page.' 
      })
      return
    }

    toast.loading({ 
      title: 'Starting Optimization', 
      description: `Running ${selectedMethod} optimization...` 
    })

    try {
      if (selectedMethod === 'vrp') {
        await dispatch(runVRPOptimization({ 
          warehouses,
          customers,
          routes: routes || []
        })).unwrap()
      } else if (selectedMethod === 'hybrid-vrp') {
        await dispatch(runHybridVRPOptimization({ 
          warehouses,
          customers,
          routes: routes || []
        })).unwrap()
      } else {
        await dispatch(runOptimization({ 
          method: selectedMethod, 
          parameters,
          warehouses,
          customers,
          routes: routes || []
        })).unwrap()
      }
      
      toast.success({ 
        title: 'Optimization Complete!', 
        description: 'Results are now available below.' 
      })
      
      if (onOptimize) {
        onOptimize()
      }
    } catch (error: any) {
      toast.error({ 
        title: 'Optimization Failed', 
        description: error?.message || 'An error occurred during optimization.' 
      })
      console.error('Optimization failed:', error)
    }
  }

  const hasData = warehouses && warehouses.length > 0 && customers && customers.length > 0
  const dataStatus = `${warehouses?.length || 0} warehouses, ${customers?.length || 0} customers`

  const getMethodDescription = () => {
    const descriptions = {
      hybrid: 'Combines classical and quantum algorithms for optimal performance and reliability.',
      quantum: 'Uses Quantum Approximate Optimization Algorithm (QAOA) for combinatorial optimization.',
      classical: 'Classical greedy algorithm for fast, reliable optimization.',
      vrp: 'Vehicle Routing Problem optimization using advanced classical algorithms.',
      'hybrid-vrp': 'Advanced VRP with hybrid quantum-classical optimization techniques.'
    }
    return descriptions[selectedMethod as keyof typeof descriptions] || 'Optimize your supply chain network.'
  }

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-2xl font-bold text-slate-200 flex items-center gap-2">
          <Database className="h-6 w-6 text-blue-400" />
          Optimization Settings
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Data Status */}
        {!hasData && (
          <Alert className="bg-yellow-500/10 border-yellow-500/30 text-yellow-400">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              No data loaded. Please add warehouse and customer data, or the system will use sample data.
            </AlertDescription>
          </Alert>
        )}

        {hasData && (
          <Alert className="bg-green-500/10 border-green-500/30 text-green-400">
            <CheckCircle2 className="h-4 w-4" />
            <AlertDescription>
              Data loaded: {dataStatus}
            </AlertDescription>
          </Alert>
        )}
        
        {error && (
          <Alert className="bg-red-500/10 border-red-500/30 text-red-400">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Method Selection */}
        <div className="space-y-3">
          <label className="text-sm font-medium text-slate-300">Optimization Method</label>
          <MethodSelector />
        </div>

        {/* Parameters Configuration */}
        <div className="space-y-3">
          <label className="text-sm font-medium text-slate-300">Parameters</label>
          <ParameterConfig />
        </div>

        {/* Progress Display */}
        {isRunning && (
          <div className="animate-in fade-in duration-300">
            <OptimizationProgress progress={progress} isRunning={isRunning} />
          </div>
        )}

        {/* Action Button */}
        <div className="flex justify-center pt-4">
          <Button
            onClick={handleStartOptimization}
            size="lg"
            disabled={!hasData && !isRunning}
            className={`
              w-full md:w-auto px-8 py-6 text-lg font-semibold
              ${isRunning 
                ? 'bg-red-600 hover:bg-red-700' 
                : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'
              }
              transition-all duration-300 hover:scale-105 active:scale-95
            `}
          >
            {isRunning ? (
              <>
                <StopCircle className="mr-2 h-5 w-5" />
                Stop Optimization
              </>
            ) : (
              <>
                <Play className="mr-2 h-5 w-5" />
                Start Optimization
              </>
            )}
          </Button>
        </div>

        {/* Method Information */}
        <Card className="bg-slate-700/30 border-slate-600">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/30 mt-0.5">
                {selectedMethod.toUpperCase()}
              </Badge>
              <div>
                <h4 className="font-medium text-slate-200 mb-1">About this method</h4>
                <p className="text-sm text-slate-400 leading-relaxed">
                  {getMethodDescription()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </CardContent>
    </Card>
  )
}

export default OptimizationPanel