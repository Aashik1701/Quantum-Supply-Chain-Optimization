import React, { useMemo } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface Assignment {
  customerId: string;
  warehouseId: string;
  co2: number;
  cost: number;
  distanceKm: number;
}

interface Co2OverlayProps {
  assignments: Assignment[];
  warehouses: Array<{ id: string; name: string }>;
  showBreakdown?: boolean;
}

const Co2Overlay: React.FC<Co2OverlayProps> = ({
  assignments,
  warehouses,
  showBreakdown = true,
}) => {
  const co2Analysis = useMemo(() => {
    const totalCo2 = assignments.reduce((sum, a) => sum + a.co2, 0);
    const totalDistance = assignments.reduce((sum, a) => sum + a.distanceKm, 0);
    const avgCo2PerKm = totalDistance > 0 ? totalCo2 / totalDistance : 0;

    // CO2 by warehouse
    const warehouseCo2 = new Map<string, number>();
    assignments.forEach(a => {
      const current = warehouseCo2.get(a.warehouseId) || 0;
      warehouseCo2.set(a.warehouseId, current + a.co2);
    });

    const warehouseBreakdown = Array.from(warehouseCo2.entries()).map(([whId, co2]) => {
      const warehouse = warehouses.find(w => w.id === whId);
      return {
        name: warehouse?.name || whId,
        value: co2,
        percentage: (co2 / totalCo2) * 100,
      };
    }).sort((a, b) => b.value - a.value);

    // CO2 intensity categories
    const lowThreshold = avgCo2PerKm * 0.8;
    const highThreshold = avgCo2PerKm * 1.2;

    const intensityBreakdown = {
      low: assignments.filter(a => (a.co2 / a.distanceKm) <= lowThreshold).reduce((sum, a) => sum + a.co2, 0),
      medium: assignments.filter(a => {
        const intensity = a.co2 / a.distanceKm;
        return intensity > lowThreshold && intensity <= highThreshold;
      }).reduce((sum, a) => sum + a.co2, 0),
      high: assignments.filter(a => (a.co2 / a.distanceKm) > highThreshold).reduce((sum, a) => sum + a.co2, 0),
    };

    return {
      totalCo2,
      totalDistance,
      avgCo2PerKm,
      warehouseBreakdown,
      intensityBreakdown,
    };
  }, [assignments, warehouses]);

  const intensityData = [
    { name: 'Low Emission', value: co2Analysis.intensityBreakdown.low, color: '#10b981' },
    { name: 'Medium Emission', value: co2Analysis.intensityBreakdown.medium, color: '#f59e0b' },
    { name: 'High Emission', value: co2Analysis.intensityBreakdown.high, color: '#ef4444' },
  ].filter(d => d.value > 0);

  const warehouseData = co2Analysis.warehouseBreakdown.map((wb, index) => ({
    ...wb,
    color: ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'][index % 5],
  }));

  if (assignments.length === 0) {
    return (
      <div className="w-full h-full bg-slate-800 rounded-lg border border-slate-700 flex items-center justify-center">
        <div className="text-center p-8">
          <div className="text-slate-500 mb-2 text-4xl">🌱</div>
          <p className="text-slate-400">No CO₂ data available</p>
          <p className="text-slate-500 text-sm mt-2">Run an optimization to see emissions</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full bg-slate-800 rounded-lg p-4 border border-slate-700 overflow-y-auto">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-200">CO₂ Emissions Analysis</h3>
        <div className="px-3 py-1 bg-green-500/20 border border-green-500/50 rounded-full text-sm text-green-300">
          🌱 Carbon Footprint
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-slate-700/30 rounded-lg p-4 text-center">
          <div className="text-xs text-slate-400 mb-1">Total CO₂</div>
          <div className="text-2xl font-bold text-slate-200">
            {co2Analysis.totalCo2.toFixed(2)}
          </div>
          <div className="text-xs text-slate-500 mt-1">kg</div>
        </div>
        <div className="bg-slate-700/30 rounded-lg p-4 text-center">
          <div className="text-xs text-slate-400 mb-1">Avg Intensity</div>
          <div className="text-2xl font-bold text-slate-200">
            {co2Analysis.avgCo2PerKm.toFixed(3)}
          </div>
          <div className="text-xs text-slate-500 mt-1">kg/km</div>
        </div>
        <div className="bg-slate-700/30 rounded-lg p-4 text-center">
          <div className="text-xs text-slate-400 mb-1">Total Distance</div>
          <div className="text-2xl font-bold text-slate-200">
            {co2Analysis.totalDistance.toFixed(0)}
          </div>
          <div className="text-xs text-slate-500 mt-1">km</div>
        </div>
      </div>

      {showBreakdown && (
        <div className="space-y-6">
          {/* Intensity Breakdown */}
          <div className="bg-slate-700/30 rounded-lg p-4">
            <h4 className="text-md font-medium text-slate-300 mb-3">Emission Intensity Distribution</h4>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={intensityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  label={(entry) => `${entry.name}: ${((entry.value / co2Analysis.totalCo2) * 100).toFixed(1)}%`}
                >
                  {intensityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '0.5rem' }}
                  formatter={(value: number) => `${value.toFixed(2)} kg`}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Warehouse Breakdown */}
          <div className="bg-slate-700/30 rounded-lg p-4">
            <h4 className="text-md font-medium text-slate-300 mb-3">CO₂ by Warehouse</h4>
            <div className="space-y-2">
              {warehouseData.map((wh, index) => (
                <div key={index} className="flex items-center gap-3">
                  <div
                    className="w-4 h-4 rounded"
                    style={{ backgroundColor: wh.color }}
                  ></div>
                  <div className="flex-1">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm text-slate-300">{wh.name}</span>
                      <span className="text-sm font-semibold text-slate-200">
                        {wh.value.toFixed(2)} kg
                      </span>
                    </div>
                    <div className="w-full bg-slate-700 rounded-full h-2">
                      <div
                        className="h-2 rounded-full transition-all"
                        style={{
                          width: `${wh.percentage}%`,
                          backgroundColor: wh.color,
                        }}
                      ></div>
                    </div>
                  </div>
                  <span className="text-xs text-slate-400 w-12 text-right">
                    {wh.percentage.toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Top Polluting Routes */}
          <div className="bg-slate-700/30 rounded-lg p-4">
            <h4 className="text-md font-medium text-slate-300 mb-3">Top 5 Emitting Routes</h4>
            <div className="space-y-2">
              {assignments
                .sort((a, b) => b.co2 - a.co2)
                .slice(0, 5)
                .map((assignment, index) => {
                  const warehouse = warehouses.find(w => w.id === assignment.warehouseId);
                  const intensity = assignment.co2 / assignment.distanceKm;
                  
                  return (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-slate-700/50 rounded border-l-4 border-red-500"
                    >
                      <div className="flex-1">
                        <div className="text-sm text-slate-300 font-medium">
                          {warehouse?.name || assignment.warehouseId} → Customer {assignment.customerId}
                        </div>
                        <div className="text-xs text-slate-500 mt-1">
                          {assignment.distanceKm.toFixed(0)} km • {intensity.toFixed(3)} kg/km
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-red-400">
                          {assignment.co2.toFixed(2)}
                        </div>
                        <div className="text-xs text-slate-500">kg CO₂</div>
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>

          {/* Environmental Impact Estimate */}
          <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
            <h4 className="text-md font-medium text-green-300 mb-2">🌍 Environmental Impact</h4>
            <div className="text-sm text-slate-300 space-y-1">
              <p>• Equivalent to {(co2Analysis.totalCo2 / 0.404).toFixed(0)} km driven by average car</p>
              <p>• Could offset with ~{(co2Analysis.totalCo2 / 21.77).toFixed(1)} tree seedlings grown for 10 years</p>
              <p>• Reduction target: Aim for {(co2Analysis.totalCo2 * 0.8).toFixed(2)} kg (-20%)</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Co2Overlay;
