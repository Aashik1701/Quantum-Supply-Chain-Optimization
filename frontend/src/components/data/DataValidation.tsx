import React from 'react'

const DataValidation: React.FC<{ validation?: any; loading?: boolean }> = ({ validation, loading }) => {
  if (loading) return <div className="text-slate-300">Validating...</div>
  if (!validation) return <div className="text-slate-400">No validation run yet.</div>
  return (
    <div className="space-y-2">
      <div className="text-green-400">Valid: {String(validation.valid)}</div>
      <div className="text-yellow-400">Warnings: {validation.warnings?.length || 0}</div>
      <div className="text-red-400">Errors: {validation.errors?.length || 0}</div>
    </div>
  )
}

export default DataValidation
