import React, { useMemo } from 'react';

interface HeatmapData {
  latitude: number;
  longitude: number;
  value: number;
  label: string;
}

interface DemandHeatmapProps {
  warehouses: Array<{ id: string; latitude: number; longitude: number; capacity: number; name: string }>;
  customers: Array<{ id: string; latitude: number; longitude: number; demand: number; name: string }>;
  assignments?: Array<{ warehouseId: string; customerId: string }>;
  metric?: 'demand' | 'capacity' | 'utilization';
}

const DemandHeatmap: React.FC<DemandHeatmapProps> = ({
  warehouses,
  customers,
  assignments = [],
  metric = 'demand',
}) => {
  const heatmapData = useMemo(() => {
    if (metric === 'demand') {
      return customers.map(c => ({
        latitude: c.latitude,
        longitude: c.longitude,
        value: c.demand,
        label: c.name,
      }));
    } else if (metric === 'capacity') {
      return warehouses.map(w => ({
        latitude: w.latitude,
        longitude: w.longitude,
        value: w.capacity,
        label: w.name,
      }));
    } else {
      // Calculate utilization per warehouse
      const warehouseLoad = new Map<string, number>();
      assignments.forEach(a => {
        const customer = customers.find(c => c.id === a.customerId);
        if (customer) {
          const current = warehouseLoad.get(a.warehouseId) || 0;
          warehouseLoad.set(a.warehouseId, current + customer.demand);
        }
      });

      return warehouses.map(w => {
        const load = warehouseLoad.get(w.id) || 0;
        const utilization = w.capacity > 0 ? (load / w.capacity) * 100 : 0;
        return {
          latitude: w.latitude,
          longitude: w.longitude,
          value: utilization,
          label: w.name,
        };
      });
    }
  }, [warehouses, customers, assignments, metric]);

  const maxValue = Math.max(...heatmapData.map(d => d.value), 1);
  const minValue = Math.min(...heatmapData.map(d => d.value), 0);

  const getColor = (value: number) => {
    const normalized = (value - minValue) / (maxValue - minValue);
    if (normalized < 0.33) {
      return { bg: 'bg-green-500', border: 'border-green-600', text: 'text-green-100' };
    } else if (normalized < 0.67) {
      return { bg: 'bg-yellow-500', border: 'border-yellow-600', text: 'text-yellow-100' };
    } else {
      return { bg: 'bg-red-500', border: 'border-red-600', text: 'text-red-100' };
    }
  };

  const formatValue = (value: number) => {
    if (metric === 'utilization') {
      return `${value.toFixed(1)}%`;
    }
    return value.toLocaleString();
  };

  const getMetricLabel = () => {
    switch (metric) {
      case 'demand':
        return 'Customer Demand';
      case 'capacity':
        return 'Warehouse Capacity';
      case 'utilization':
        return 'Warehouse Utilization';
      default:
        return 'Value';
    }
  };

  return (
    <div className="w-full h-full bg-slate-800 rounded-lg p-4 border border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-200">{getMetricLabel()} Heatmap</h3>
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span>Low</span>
          <div className="flex gap-0.5">
            <div className="w-4 h-4 bg-green-500"></div>
            <div className="w-4 h-4 bg-yellow-500"></div>
            <div className="w-4 h-4 bg-red-500"></div>
          </div>
          <span>High</span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 max-h-[calc(100%-4rem)] overflow-y-auto">
        {heatmapData.map((point, index) => {
          const colors = getColor(point.value);
          const size = Math.max(60, Math.min(120, (point.value / maxValue) * 100));

          return (
            <div
              key={index}
              className={`relative p-3 rounded-lg border-2 ${colors.border} ${colors.bg} bg-opacity-20 hover:bg-opacity-30 transition-all cursor-pointer`}
              style={{
                minHeight: `${size}px`,
              }}
            >
              <div className="flex flex-col h-full justify-between">
                <div className={`text-xs font-medium ${colors.text} mb-1 line-clamp-2`}>
                  {point.label}
                </div>
                <div className={`text-2xl font-bold ${colors.text}`}>
                  {formatValue(point.value)}
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  {point.latitude.toFixed(2)}, {point.longitude.toFixed(2)}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-4 grid grid-cols-3 gap-4 text-center text-sm">
        <div className="bg-slate-700/50 rounded p-2">
          <div className="text-slate-400">Total Points</div>
          <div className="text-xl font-bold text-slate-200">{heatmapData.length}</div>
        </div>
        <div className="bg-slate-700/50 rounded p-2">
          <div className="text-slate-400">Max Value</div>
          <div className="text-xl font-bold text-slate-200">{formatValue(maxValue)}</div>
        </div>
        <div className="bg-slate-700/50 rounded p-2">
          <div className="text-slate-400">Avg Value</div>
          <div className="text-xl font-bold text-slate-200">
            {formatValue(heatmapData.reduce((sum, d) => sum + d.value, 0) / heatmapData.length)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DemandHeatmap;
