import React from 'react'
import { useSelector } from 'react-redux'
import { RootState } from '../../store'

interface ResultsPanelProps {
  className?: string
}

const ResultsPanel: React.FC<ResultsPanelProps> = ({ className = '' }) => {
  const { results, isRunning } = useSelector((state: RootState) => state.optimization)

  if (isRunning) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Optimization Results</h2>
        <div className="flex items-center justify-center h-48">
          <div className="text-gray-500">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p>Optimization in progress...</p>
          </div>
        </div>
      </div>
    )
  }

  if (!results) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Optimization Results</h2>
        <div className="flex items-center justify-center h-48">
          <div className="text-gray-500 text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <p className="mt-2">No optimization results yet</p>
            <p className="text-sm text-gray-400">Run an optimization to see results here</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Optimization Results</h2>
      
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-blue-800">Total Cost</h3>
          <p className="text-2xl font-bold text-blue-900">
            ${results.total_cost?.toFixed(2) || 'N/A'}
          </p>
        </div>
        
        <div className="bg-green-50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-green-800">CO2 Emissions</h3>
          <p className="text-2xl font-bold text-green-900">
            {results.total_co2?.toFixed(2) || 'N/A'} kg
          </p>
        </div>
        
        <div className="bg-purple-50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-purple-800">Avg Delivery Time</h3>
          <p className="text-2xl font-bold text-purple-900">
            {results.avg_delivery_time?.toFixed(1) || 'N/A'} hours
          </p>
        </div>
      </div>

      {/* Method and Performance */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Optimization Details</h3>
          <span className="px-3 py-1 bg-gray-100 text-gray-800 text-sm rounded-full">
            Method: {results.method || 'Unknown'}
          </span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Routes Used</p>
            <p className="text-lg font-medium">{results.routes_used || 0}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Execution Time</p>
            <p className="text-lg font-medium">
              {results.performance_metrics?.optimization_time_seconds?.toFixed(2) || 'N/A'}s
            </p>
          </div>
        </div>
      </div>

      {/* Routes Table */}
      {results.routes && results.routes.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Route Details</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Route
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Distance (km)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cost
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    CO2 (kg)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Delivery Time (h)
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {results.routes.slice(0, 10).map((route: any, index: number) => (
                  <tr key={route.id || index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {route.warehouse_id} → {route.customer_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {route.distance_km?.toFixed(1) || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      ${route.total_cost?.toFixed(2) || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {route.total_co2?.toFixed(2) || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {route.delivery_time_hours?.toFixed(1) || 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {results.routes.length > 10 && (
            <p className="text-sm text-gray-500 mt-2">
              Showing first 10 of {results.routes.length} routes
            </p>
          )}
        </div>
      )}
    </div>
  )
}

export default ResultsPanel