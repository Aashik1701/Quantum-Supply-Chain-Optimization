import React from 'react'
import { useSelector } from 'react-redux'
import { RootState } from '../../store'
import { CardSkeleton } from '../ui/loading-skeleton'
import { EmptyState } from '../ui/empty-state'
import { BarChart3, DollarSign, Leaf, Clock, TrendingUp, CheckCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'

interface ResultsPanelProps {
  className?: string
}

const ResultsPanel: React.FC<ResultsPanelProps> = ({ className = '' }) => {
  const { results, isRunning } = useSelector((state: RootState) => state.optimization)

  if (isRunning) {
    return (
      <div className={className}>
        <CardSkeleton />
      </div>
    )
  }

  if (!results) {
    return (
      <Card className={`bg-slate-800 border-slate-700 ${className}`}>
        <CardContent className="pt-6">
          <EmptyState
            icon={BarChart3}
            title="No optimization results yet"
            description="Run an optimization to see detailed results, metrics, and route assignments here"
          />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={`bg-slate-800 border-slate-700 ${className}`}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-2xl font-bold text-slate-200 flex items-center gap-2">
            <CheckCircle className="h-6 w-6 text-green-500" />
            Optimization Results
          </CardTitle>
          <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/30">
            {results.method || 'Unknown'} Method
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="bg-gradient-to-br from-blue-500/10 to-blue-600/5 border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/20 transition-all">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-blue-500/20 rounded-lg">
                  <DollarSign className="h-5 w-5 text-blue-400" />
                </div>
                <h3 className="text-sm font-medium text-slate-400">Total Cost</h3>
              </div>
              <p className="text-3xl font-bold text-blue-400">
                ${(results.totalCost || results.total_cost || 0).toFixed(2)}
              </p>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-green-500/10 to-green-600/5 border-green-500/30 hover:shadow-lg hover:shadow-green-500/20 transition-all">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-green-500/20 rounded-lg">
                  <Leaf className="h-5 w-5 text-green-400" />
                </div>
                <h3 className="text-sm font-medium text-slate-400">CO2 Emissions</h3>
              </div>
              <p className="text-3xl font-bold text-green-400">
                {(results.totalCo2 || results.total_co2 || 0).toFixed(2)} <span className="text-xl">kg</span>
              </p>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-purple-500/10 to-purple-600/5 border-purple-500/30 hover:shadow-lg hover:shadow-purple-500/20 transition-all">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-purple-500/20 rounded-lg">
                  <Clock className="h-5 w-5 text-purple-400" />
                </div>
                <h3 className="text-sm font-medium text-slate-400">Avg Delivery Time</h3>
              </div>
              <p className="text-3xl font-bold text-purple-400">
                {(results.avgDeliveryTime || results.avg_delivery_time || 0).toFixed(2)} <span className="text-xl">hrs</span>
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Performance Metrics */}
        <Card className="bg-slate-700/30 border-slate-600">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2 text-slate-200">
              <TrendingUp className="h-5 w-5 text-blue-400" />
              Performance Metrics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-slate-400 mb-1">Routes Used</p>
                <p className="text-2xl font-bold text-slate-200">{results.routesUsed || results.routes_used || 0}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400 mb-1">Execution Time</p>
                <p className="text-2xl font-bold text-slate-200">
                  {(results.performanceMetrics?.optimizationTimeSeconds || 
                    results.performance_metrics?.optimization_time_seconds || 0).toFixed(3)}<span className="text-sm">s</span>
                </p>
              </div>
              <div>
                <p className="text-sm text-slate-400 mb-1">Assignments</p>
                <p className="text-2xl font-bold text-slate-200">{results.assignments?.length || 0}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400 mb-1">Method</p>
                <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30 mt-1">
                  {results.method || 'N/A'}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Routes Table */}
        {results.routes && results.routes.length > 0 && (
          <Card className="bg-slate-700/30 border-slate-600">
            <CardHeader>
              <CardTitle className="text-lg text-slate-200">Route Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-600">
                  <thead className="bg-slate-800/50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                        Route
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                        Distance (km)
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                        Cost
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                        CO2 (kg)
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                        Delivery Time (h)
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-600">
                    {results.routes.slice(0, 10).map((route: any, index: number) => (
                      <tr key={route.id || index} className="hover:bg-slate-700/30 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-200">
                          {route.warehouse_id} → {route.customer_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                          {route.distance_km?.toFixed(1) || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-400 font-medium">
                          ${route.total_cost?.toFixed(2) || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-green-400 font-medium">
                          {route.total_co2?.toFixed(2) || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-purple-400 font-medium">
                          {route.delivery_time_hours?.toFixed(1) || 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {results.routes.length > 10 && (
                <p className="text-sm text-slate-400 mt-4 text-center">
                  Showing first 10 of {results.routes.length} routes
                </p>
              )}
            </CardContent>
          </Card>
        )}
      </CardContent>
    </Card>
  )
}

export default ResultsPanel