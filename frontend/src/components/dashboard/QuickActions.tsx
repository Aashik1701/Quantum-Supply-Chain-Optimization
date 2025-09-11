import React from 'react'

const QuickActions: React.FC = () => {
  return (
    <div className="bg-slate-800 rounded-lg shadow-sm border border-slate-700 p-4 flex flex-wrap gap-3">
      {[
        { label: 'Start Optimization', color: 'btn-primary' },
        { label: 'Upload Data', color: 'btn-secondary' },
        { label: 'View Results', color: 'btn-secondary' },
      ].map((a) => (
        <button key={a.label} className={`${a.color}`}>
          {a.label}
        </button>
      ))}
    </div>
  )
}

export default QuickActions
