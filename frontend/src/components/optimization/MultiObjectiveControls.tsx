import React, { useState, useCallback } from 'react';
import { Sliders, Play, Save, RotateCcw } from 'lucide-react';

interface Weights {
  cost: number;
  co2: number;
  time: number;
}

interface MultiObjectiveControlsProps {
  onOptimize: (weights: Weights) => void;
  onSavePreset?: (name: string, weights: Weights) => void;
  savedPresets?: Array<{ name: string; weights: Weights }>;
  isOptimizing?: boolean;
}

const MultiObjectiveControls: React.FC<MultiObjectiveControlsProps> = ({
  onOptimize,
  onSavePreset,
  savedPresets = [],
  isOptimizing = false,
}) => {
  // Default balanced weights
  const defaultWeights: Weights = { cost: 0.33, co2: 0.33, time: 0.34 };
  
  const [weights, setWeights] = useState<Weights>(defaultWeights);
  const [presetName, setPresetName] = useState('');
  const [showSaveDialog, setShowSaveDialog] = useState(false);

  // Normalize weights to sum to 1
  const normalizeWeights = useCallback((w: Weights): Weights => {
    const sum = w.cost + w.co2 + w.time;
    if (sum === 0) return defaultWeights;
    return {
      cost: w.cost / sum,
      co2: w.co2 / sum,
      time: w.time / sum,
    };
  }, []);

  const handleWeightChange = useCallback((objective: keyof Weights, value: number) => {
    setWeights(prev => {
      const updated = { ...prev, [objective]: value };
      return normalizeWeights(updated);
    });
  }, [normalizeWeights]);

  const handleOptimize = useCallback(() => {
    onOptimize(weights);
  }, [onOptimize, weights]);

  const handleReset = useCallback(() => {
    setWeights(defaultWeights);
  }, []);

  const handleSavePreset = useCallback(() => {
    if (presetName.trim() && onSavePreset) {
      onSavePreset(presetName.trim(), weights);
      setPresetName('');
      setShowSaveDialog(false);
    }
  }, [presetName, weights, onSavePreset]);

  const handleLoadPreset = useCallback((preset: { name: string; weights: Weights }) => {
    setWeights(preset.weights);
  }, []);

  // Preset configurations
  const quickPresets: Array<{ name: string; weights: Weights; icon: string }> = [
    { name: 'Cost Priority', weights: { cost: 0.7, co2: 0.15, time: 0.15 }, icon: '💰' },
    { name: 'Green Priority', weights: { cost: 0.15, co2: 0.7, time: 0.15 }, icon: '🌱' },
    { name: 'Speed Priority', weights: { cost: 0.15, co2: 0.15, time: 0.7 }, icon: '⚡' },
    { name: 'Balanced', weights: { cost: 0.33, co2: 0.33, time: 0.34 }, icon: '⚖️' },
  ];

  return (
    <div className="bg-gray-800 rounded-lg p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Sliders className="w-5 h-5 text-blue-400" />
          <h3 className="text-lg font-semibold text-white">Multi-Objective Optimization</h3>
        </div>
        <button
          onClick={handleReset}
          className="flex items-center space-x-1 px-3 py-1 text-sm text-gray-400 hover:text-white transition-colors"
          title="Reset to balanced weights"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Reset</span>
        </button>
      </div>

      {/* Weight Sliders */}
      <div className="space-y-4">
        {/* Cost Weight */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="text-sm font-medium text-gray-300">Cost Weight</label>
            <span className="text-sm font-mono text-blue-400">{(weights.cost * 100).toFixed(1)}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            step="1"
            value={weights.cost * 100}
            onChange={(e) => handleWeightChange('cost', parseFloat(e.target.value) / 100)}
            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            disabled={isOptimizing}
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Min Cost</span>
            <span>Ignore Cost</span>
          </div>
        </div>

        {/* CO2 Weight */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="text-sm font-medium text-gray-300">CO₂ Emissions Weight</label>
            <span className="text-sm font-mono text-green-400">{(weights.co2 * 100).toFixed(1)}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            step="1"
            value={weights.co2 * 100}
            onChange={(e) => handleWeightChange('co2', parseFloat(e.target.value) / 100)}
            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-green-500"
            disabled={isOptimizing}
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Min Emissions</span>
            <span>Ignore Emissions</span>
          </div>
        </div>

        {/* Time Weight */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="text-sm font-medium text-gray-300">Delivery Time Weight</label>
            <span className="text-sm font-mono text-purple-400">{(weights.time * 100).toFixed(1)}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            step="1"
            value={weights.time * 100}
            onChange={(e) => handleWeightChange('time', parseFloat(e.target.value) / 100)}
            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
            disabled={isOptimizing}
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Min Time</span>
            <span>Ignore Time</span>
          </div>
        </div>
      </div>

      {/* Quick Presets */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">Quick Presets</label>
        <div className="grid grid-cols-2 gap-2">
          {quickPresets.map((preset) => (
            <button
              key={preset.name}
              onClick={() => handleLoadPreset(preset)}
              className="flex items-center space-x-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-left"
              disabled={isOptimizing}
            >
              <span className="text-lg">{preset.icon}</span>
              <span className="text-sm text-white">{preset.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Saved Presets */}
      {savedPresets.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Saved Presets</label>
          <div className="space-y-2">
            {savedPresets.map((preset, index) => (
              <button
                key={index}
                onClick={() => handleLoadPreset(preset)}
                className="w-full flex items-center justify-between px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                disabled={isOptimizing}
              >
                <span className="text-sm text-white">{preset.name}</span>
                <span className="text-xs text-gray-400">
                  {(preset.weights.cost * 100).toFixed(0)}/{(preset.weights.co2 * 100).toFixed(0)}/{(preset.weights.time * 100).toFixed(0)}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Save Preset Dialog */}
      {showSaveDialog ? (
        <div className="space-y-2">
          <input
            type="text"
            value={presetName}
            onChange={(e) => setPresetName(e.target.value)}
            placeholder="Preset name..."
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
            onKeyDown={(e) => e.key === 'Enter' && handleSavePreset()}
          />
          <div className="flex space-x-2">
            <button
              onClick={handleSavePreset}
              className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              disabled={!presetName.trim()}
            >
              Save
            </button>
            <button
              onClick={() => {
                setShowSaveDialog(false);
                setPresetName('');
              }}
              className="flex-1 px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setShowSaveDialog(true)}
          className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
          disabled={isOptimizing}
        >
          <Save className="w-4 h-4" />
          <span>Save Current Weights</span>
        </button>
      )}

      {/* Optimize Button */}
      <button
        onClick={handleOptimize}
        disabled={isOptimizing}
        className={`w-full flex items-center justify-center space-x-2 px-6 py-3 rounded-lg font-semibold transition-all ${
          isOptimizing
            ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
            : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg'
        }`}
      >
        <Play className="w-5 h-5" />
        <span>{isOptimizing ? 'Optimizing...' : 'Run Optimization'}</span>
      </button>

      {/* Weight Summary */}
      <div className="pt-4 border-t border-gray-700">
        <div className="text-xs text-gray-400 space-y-1">
          <p className="font-semibold text-gray-300 mb-2">Current Configuration:</p>
          <p>• Cost priority: {(weights.cost * 100).toFixed(1)}% influence</p>
          <p>• CO₂ priority: {(weights.co2 * 100).toFixed(1)}% influence</p>
          <p>• Time priority: {(weights.time * 100).toFixed(1)}% influence</p>
          <p className="mt-2 text-gray-500 italic">
            Weights are automatically normalized to sum to 100%
          </p>
        </div>
      </div>
    </div>
  );
};

export default MultiObjectiveControls;
