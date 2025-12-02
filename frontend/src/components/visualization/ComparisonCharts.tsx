import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

interface OptimizationResult {
  method: string;
  totalCost: number;
  totalCo2: number;
  avgDeliveryTime: number;
  routesUsed: number;
  optimizationTime: number;
}

interface ComparisonChartsProps {
  results: OptimizationResult[];
  showCost?: boolean;
  showCo2?: boolean;
  showTime?: boolean;
  showRoutes?: boolean;
}

const ComparisonCharts: React.FC<ComparisonChartsProps> = ({
  results,
  showCost = true,
  showCo2 = true,
  showTime = true,
  showRoutes = true,
}) => {
  if (results.length === 0) {
    return (
      <div className="w-full h-full bg-slate-800 rounded-lg border border-slate-700 flex items-center justify-center">
        <div className="text-center p-8">
          <div className="text-slate-500 mb-2 text-4xl">📊</div>
          <p className="text-slate-400">No results to compare</p>
          <p className="text-slate-500 text-sm mt-2">Run multiple optimizations to see comparisons</p>
        </div>
      </div>
    );
  }

  const costData = results.map(r => ({
    name: r.method.charAt(0).toUpperCase() + r.method.slice(1),
    cost: r.totalCost,
  }));

  const co2Data = results.map(r => ({
    name: r.method.charAt(0).toUpperCase() + r.method.slice(1),
    co2: r.totalCo2,
  }));

  const timeData = results.map(r => ({
    name: r.method.charAt(0).toUpperCase() + r.method.slice(1),
    deliveryTime: r.avgDeliveryTime,
    optimizationTime: r.optimizationTime,
  }));

  const routesData = results.map(r => ({
    name: r.method.charAt(0).toUpperCase() + r.method.slice(1),
    routes: r.routesUsed,
  }));

  return (
    <div className="w-full h-full bg-slate-800 rounded-lg p-4 border border-slate-700 overflow-y-auto">
      <h3 className="text-lg font-semibold text-slate-200 mb-4">Optimization Comparison</h3>

      <div className="space-y-6">
        {showCost && (
          <div className="bg-slate-700/30 rounded-lg p-4">
            <h4 className="text-md font-medium text-slate-300 mb-3">Total Cost</h4>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={costData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '0.5rem' }}
                  labelStyle={{ color: '#e2e8f0' }}
                />
                <Legend wrapperStyle={{ color: '#9ca3af' }} />
                <Bar dataKey="cost" fill="#3b82f6" name="Cost ($)" />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-2 text-sm text-slate-400">
              Best: {Math.min(...costData.map(d => d.cost)).toFixed(2)} | 
              Worst: {Math.max(...costData.map(d => d.cost)).toFixed(2)}
            </div>
          </div>
        )}

        {showCo2 && (
          <div className="bg-slate-700/30 rounded-lg p-4">
            <h4 className="text-md font-medium text-slate-300 mb-3">CO₂ Emissions</h4>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={co2Data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '0.5rem' }}
                  labelStyle={{ color: '#e2e8f0' }}
                />
                <Legend wrapperStyle={{ color: '#9ca3af' }} />
                <Bar dataKey="co2" fill="#10b981" name="CO₂ (kg)" />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-2 text-sm text-slate-400">
              Best: {Math.min(...co2Data.map(d => d.co2)).toFixed(2)} kg | 
              Worst: {Math.max(...co2Data.map(d => d.co2)).toFixed(2)} kg
            </div>
          </div>
        )}

        {showTime && (
          <div className="bg-slate-700/30 rounded-lg p-4">
            <h4 className="text-md font-medium text-slate-300 mb-3">Time Metrics</h4>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={timeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '0.5rem' }}
                  labelStyle={{ color: '#e2e8f0' }}
                />
                <Legend wrapperStyle={{ color: '#9ca3af' }} />
                <Line type="monotone" dataKey="deliveryTime" stroke="#f59e0b" name="Avg Delivery (hrs)" strokeWidth={2} />
                <Line type="monotone" dataKey="optimizationTime" stroke="#ec4899" name="Optimization (s)" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {showRoutes && (
          <div className="bg-slate-700/30 rounded-lg p-4">
            <h4 className="text-md font-medium text-slate-300 mb-3">Routes Used</h4>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={routesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '0.5rem' }}
                  labelStyle={{ color: '#e2e8f0' }}
                />
                <Legend wrapperStyle={{ color: '#9ca3af' }} />
                <Bar dataKey="routes" fill="#8b5cf6" name="Routes" />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-2 text-sm text-slate-400">
              Avg: {(routesData.reduce((sum, d) => sum + d.routes, 0) / routesData.length).toFixed(1)} routes
            </div>
          </div>
        )}

        {/* Summary Table */}
        <div className="bg-slate-700/30 rounded-lg p-4 overflow-x-auto">
          <h4 className="text-md font-medium text-slate-300 mb-3">Summary Table</h4>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-600">
                <th className="text-left py-2 px-3 text-slate-400">Method</th>
                <th className="text-right py-2 px-3 text-slate-400">Cost</th>
                <th className="text-right py-2 px-3 text-slate-400">CO₂</th>
                <th className="text-right py-2 px-3 text-slate-400">Delivery</th>
                <th className="text-right py-2 px-3 text-slate-400">Routes</th>
                <th className="text-right py-2 px-3 text-slate-400">Time</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result, index) => (
                <tr key={index} className="border-b border-slate-700/50 hover:bg-slate-700/20">
                  <td className="py-2 px-3 text-slate-300 font-medium">
                    {result.method.charAt(0).toUpperCase() + result.method.slice(1)}
                  </td>
                  <td className="text-right py-2 px-3 text-slate-300">${result.totalCost.toFixed(2)}</td>
                  <td className="text-right py-2 px-3 text-slate-300">{result.totalCo2.toFixed(2)} kg</td>
                  <td className="text-right py-2 px-3 text-slate-300">{result.avgDeliveryTime.toFixed(1)} hrs</td>
                  <td className="text-right py-2 px-3 text-slate-300">{result.routesUsed}</td>
                  <td className="text-right py-2 px-3 text-slate-300">{result.optimizationTime.toFixed(2)}s</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Winner Analysis */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-blue-500/20 border border-blue-500/50 rounded-lg p-3 text-center">
            <div className="text-xs text-blue-300 mb-1">Best Cost</div>
            <div className="text-sm font-bold text-blue-200">
              {results.reduce((best, r) => r.totalCost < best.totalCost ? r : best).method}
            </div>
          </div>
          <div className="bg-green-500/20 border border-green-500/50 rounded-lg p-3 text-center">
            <div className="text-xs text-green-300 mb-1">Best CO₂</div>
            <div className="text-sm font-bold text-green-200">
              {results.reduce((best, r) => r.totalCo2 < best.totalCo2 ? r : best).method}
            </div>
          </div>
          <div className="bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-3 text-center">
            <div className="text-xs text-yellow-300 mb-1">Best Delivery</div>
            <div className="text-sm font-bold text-yellow-200">
              {results.reduce((best, r) => r.avgDeliveryTime < best.avgDeliveryTime ? r : best).method}
            </div>
          </div>
          <div className="bg-purple-500/20 border border-purple-500/50 rounded-lg p-3 text-center">
            <div className="text-xs text-purple-300 mb-1">Fastest Solve</div>
            <div className="text-sm font-bold text-purple-200">
              {results.reduce((best, r) => r.optimizationTime < best.optimizationTime ? r : best).method}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComparisonCharts;
