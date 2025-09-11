import React from 'react'

interface Props { data?: any }

const DashboardStats: React.FC<Props> = ({ data }) => {
  const stats = data || {
    activeOptimizations: 0,
    monthlySavings: 0,
    efficiencyGain: 0,
  }
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
      <div className="p-6 border rounded-lg shadow-sm bg-slate-800 border-slate-700">
        <h3 className="text-lg font-semibold text-slate-200">Active Optimizations</h3>
        <p className="mt-2 text-3xl font-bold text-blue-400">{stats.activeOptimizations}</p>
        <p className="text-sm text-slate-400">Running processes</p>
      </div>
      <div className="p-6 border rounded-lg shadow-sm bg-slate-800 border-slate-700">
        <h3 className="text-lg font-semibold text-slate-200">Cost Savings</h3>
        <p className="mt-2 text-3xl font-bold text-green-400">${stats.monthlySavings}</p>
        <p className="text-sm text-slate-400">This month</p>
      </div>
      <div className="p-6 border rounded-lg shadow-sm bg-slate-800 border-slate-700">
        <h3 className="text-lg font-semibold text-slate-200">Efficiency Gain</h3>
        <p className="mt-2 text-3xl font-bold text-purple-400">{stats.efficiencyGain}%</p>
        <p className="text-sm text-slate-400">Compared to baseline</p>
      </div>
    </div>
  )
}

export default DashboardStats
