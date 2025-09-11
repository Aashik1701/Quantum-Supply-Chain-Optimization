import React from 'react'

const OptimizationProgress: React.FC<{ progress: number; isRunning: boolean }> = ({ progress, isRunning }) => {
  return (
    <div>
      <div className="flex justify-between text-sm mb-2">
        <span className="text-slate-400">Progress</span>
        <span className="text-slate-200">{progress}%</span>
      </div>
      <div className="w-full bg-slate-700 rounded-full h-2">
        <div className={`h-2 rounded-full transition-all duration-300 ${isRunning ? 'bg-blue-500' : 'bg-slate-500'}`} style={{ width: `${progress}%` }} />
      </div>
    </div>
  )
}

export default OptimizationProgress
