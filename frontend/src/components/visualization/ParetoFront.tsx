import React, { useMemo, useState } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ZAxis } from 'recharts';
import { TrendingUp, Filter, Download } from 'lucide-react';

interface Solution {
  id: string;
  cost: number;
  co2: number;
  time: number;
  method: string;
  weights?: { cost: number; co2: number; time: number };
  isDominated: boolean;
  routes?: any[];
}

interface ParetoFrontProps {
  solutions: Solution[];
  onSelectSolution?: (solution: Solution) => void;
  selectedSolutionId?: string;
}

type Axis = 'cost' | 'co2' | 'time';

const ParetoFront: React.FC<ParetoFrontProps> = ({
  solutions,
  onSelectSolution,
  selectedSolutionId,
}) => {
  const [xAxis, setXAxis] = useState<Axis>('cost');
  const [yAxis, setYAxis] = useState<Axis>('co2');
  const [showDominated, setShowDominated] = useState(false);

  // Filter solutions based on dominance
  const filteredSolutions = useMemo(() => {
    return showDominated ? solutions : solutions.filter(s => !s.isDominated);
  }, [solutions, showDominated]);

  // Pareto front (non-dominated solutions)
  const paretoSolutions = useMemo(() => {
    return solutions.filter(s => !s.isDominated);
  }, [solutions]);

  // Transform solutions for scatter chart
  const chartData = useMemo(() => {
    return filteredSolutions.map(solution => ({
      x: solution[xAxis],
      y: solution[yAxis],
      z: solution.time, // Size indicator
      id: solution.id,
      method: solution.method,
      isDominated: solution.isDominated,
      isSelected: solution.id === selectedSolutionId,
      solution,
    }));
  }, [filteredSolutions, xAxis, yAxis, selectedSolutionId]);

  // Axis labels
  const axisLabels: Record<Axis, string> = {
    cost: 'Total Cost ($)',
    co2: 'CO₂ Emissions (kg)',
    time: 'Delivery Time (hours)',
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length > 0) {
      const data = payload[0].payload;
      const solution = data.solution;
      
      return (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 shadow-xl">
          <p className="text-sm font-semibold text-white mb-2">
            {solution.method.toUpperCase()} Solution
          </p>
          <div className="space-y-1 text-xs">
            <p className="text-blue-400">Cost: ${solution.cost.toFixed(2)}</p>
            <p className="text-green-400">CO₂: {solution.co2.toFixed(2)} kg</p>
            <p className="text-purple-400">Time: {solution.time.toFixed(2)} hrs</p>
            {solution.weights && (
              <p className="text-gray-400 mt-2 pt-2 border-t border-gray-700">
                Weights: {(solution.weights.cost * 100).toFixed(0)}/
                {(solution.weights.co2 * 100).toFixed(0)}/
                {(solution.weights.time * 100).toFixed(0)}
              </p>
            )}
            {solution.isDominated && (
              <p className="text-red-400 mt-2">⚠️ Dominated</p>
            )}
            {data.isSelected && (
              <p className="text-yellow-400 mt-2">✓ Selected</p>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  // Export Pareto front data
  const handleExport = () => {
    const data = paretoSolutions.map(s => ({
      id: s.id,
      method: s.method,
      cost: s.cost,
      co2: s.co2,
      time: s.time,
      weights: s.weights,
    }));
    
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pareto-front-${new Date().toISOString()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Statistics
  const stats = useMemo(() => {
    if (paretoSolutions.length === 0) return null;
    
    const costs = paretoSolutions.map(s => s.cost);
    const co2s = paretoSolutions.map(s => s.co2);
    const times = paretoSolutions.map(s => s.time);
    
    return {
      paretoCount: paretoSolutions.length,
      totalCount: solutions.length,
      dominatedCount: solutions.length - paretoSolutions.length,
      costRange: { min: Math.min(...costs), max: Math.max(...costs) },
      co2Range: { min: Math.min(...co2s), max: Math.max(...co2s) },
      timeRange: { min: Math.min(...times), max: Math.max(...times) },
    };
  }, [paretoSolutions, solutions]);

  return (
    <div className="bg-gray-800 rounded-lg p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <TrendingUp className="w-5 h-5 text-purple-400" />
          <h3 className="text-lg font-semibold text-white">Pareto Front Analysis</h3>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleExport}
            className="flex items-center space-x-1 px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
            disabled={paretoSolutions.length === 0}
          >
            <Download className="w-4 h-4" />
            <span className="text-sm">Export</span>
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* X Axis Selector */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">X Axis</label>
          <select
            value={xAxis}
            onChange={(e) => setXAxis(e.target.value as Axis)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
          >
            <option value="cost">Cost ($)</option>
            <option value="co2">CO₂ Emissions (kg)</option>
            <option value="time">Delivery Time (hrs)</option>
          </select>
        </div>

        {/* Y Axis Selector */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Y Axis</label>
          <select
            value={yAxis}
            onChange={(e) => setYAxis(e.target.value as Axis)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
          >
            <option value="cost">Cost ($)</option>
            <option value="co2">CO₂ Emissions (kg)</option>
            <option value="time">Delivery Time (hrs)</option>
          </select>
        </div>

        {/* Show Dominated Toggle */}
        <div className="flex items-end">
          <label className="flex items-center space-x-2 px-3 py-2 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition-colors">
            <input
              type="checkbox"
              checked={showDominated}
              onChange={(e) => setShowDominated(e.target.checked)}
              className="w-4 h-4 text-blue-600 bg-gray-800 border-gray-600 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-white">Show Dominated</span>
          </label>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-gray-900 rounded-lg p-4" style={{ height: '400px' }}>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart
              margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis
                type="number"
                dataKey="x"
                name={axisLabels[xAxis]}
                stroke="#9CA3AF"
                label={{ value: axisLabels[xAxis], position: 'insideBottom', offset: -10, fill: '#9CA3AF' }}
              />
              <YAxis
                type="number"
                dataKey="y"
                name={axisLabels[yAxis]}
                stroke="#9CA3AF"
                label={{ value: axisLabels[yAxis], angle: -90, position: 'insideLeft', fill: '#9CA3AF' }}
              />
              <ZAxis type="number" dataKey="z" range={[50, 400]} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              
              {/* Pareto solutions */}
              <Scatter
                name="Pareto Front"
                data={chartData.filter(d => !d.isDominated)}
                fill="#8B5CF6"
                onClick={(data) => onSelectSolution && onSelectSolution(data.solution)}
                cursor="pointer"
              />
              
              {/* Dominated solutions (if shown) */}
              {showDominated && (
                <Scatter
                  name="Dominated"
                  data={chartData.filter(d => d.isDominated)}
                  fill="#6B7280"
                  onClick={(data) => onSelectSolution && onSelectSolution(data.solution)}
                  cursor="pointer"
                />
              )}
              
              {/* Selected solution highlight */}
              {selectedSolutionId && (
                <Scatter
                  name="Selected"
                  data={chartData.filter(d => d.isSelected)}
                  fill="#FBBF24"
                  shape="star"
                />
              )}
            </ScatterChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-400">No solutions to display. Run optimizations with different weight configurations.</p>
          </div>
        )}
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Pareto Solutions Count */}
          <div className="bg-gray-900 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">Pareto Solutions</span>
              <Filter className="w-4 h-4 text-purple-400" />
            </div>
            <p className="text-2xl font-bold text-white">{stats.paretoCount}</p>
            <p className="text-xs text-gray-500 mt-1">
              {stats.dominatedCount} dominated out of {stats.totalCount}
            </p>
          </div>

          {/* Cost Range */}
          <div className="bg-gray-900 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">Cost Range</span>
              <span className="text-xs text-blue-400">$</span>
            </div>
            <p className="text-lg font-bold text-white">
              ${stats.costRange.min.toFixed(0)} - ${stats.costRange.max.toFixed(0)}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Spread: ${(stats.costRange.max - stats.costRange.min).toFixed(0)}
            </p>
          </div>

          {/* CO2 Range */}
          <div className="bg-gray-900 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">CO₂ Range</span>
              <span className="text-xs text-green-400">kg</span>
            </div>
            <p className="text-lg font-bold text-white">
              {stats.co2Range.min.toFixed(0)} - {stats.co2Range.max.toFixed(0)} kg
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Spread: {(stats.co2Range.max - stats.co2Range.min).toFixed(0)} kg
            </p>
          </div>
        </div>
      )}

      {/* Info Panel */}
      <div className="bg-gray-900 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-white mb-2">About Pareto Optimality</h4>
        <div className="text-xs text-gray-400 space-y-2">
          <p>
            <span className="text-purple-400 font-semibold">Pareto Front:</span> Solutions where no objective can be improved without worsening another.
          </p>
          <p>
            <span className="text-gray-500 font-semibold">Dominated Solutions:</span> Solutions where at least one other solution is better in all objectives.
          </p>
          <p>
            • Adjust weights to explore different trade-offs between cost, emissions, and delivery time.
          </p>
          <p>
            • Click points to select and view detailed solution information.
          </p>
          <p>
            • Point size represents the third dimension (delivery time) for 3D visualization.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ParetoFront;
